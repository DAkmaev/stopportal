<template>
  <div>
    <v-container fluid>
      <v-row class="justify">
        <v-col cols="6" />
        <v-col />
        <v-col cols="3" align="right">
          <v-row>
            <v-col>
              <v-text-field :value="sumPrice" label="Портфель" readonly style="width: 100px" />
            </v-col>
            <v-col>
              <v-text-field :value="fillUp" label="Доливка" style="width: 100px" @change="changeFillUp" />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            dense
            :disable-pagination="true"
            :items="list"
            :headers="headers"
            :loading="loading"
          >
            <template v-slot:item.weight="{ item }">
              <span v-if="item.weight" :class="getRatingColor(item.weight, 1) + '--text font-weight-bold'">{{ item.weight }}%</span>
            </template>
            <template v-slot:item.total_rating="{ item }">
              <span v-if="item.total_rating" :class="getRatingColor(item.weight, 1) + '--text font-weight-bold'">{{ item.total_rating }}</span>
            </template>
            <template v-slot:item.exist_part="{ item }">
              <span v-if="item.exist_part">{{ item.exist_part }}%</span>
            </template>
            <template v-slot:item.part_briefcase="{ item }">
              <span v-if="item.part_briefcase">{{ item.part_briefcase }}%</span>
            </template>
            <template v-slot:item.lots_to_buy_fact="{ item }">
              <v-edit-dialog
                :return-value.sync="item.lots_to_buy_fact"
                @save="saveRatingBriefcaseValue(item)"
              >
                {{ item.lots_to_buy_fact }}
                <template v-slot:input>
                  <v-text-field
                    v-model="item.lots_to_buy_fact"
                    label="Изменить"
                    single-line
                  />
                </template>
              </v-edit-dialog>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>

import { getData, putData, postData, deleteData, endpoints } from '@/api/invmos-back'
import { getRatingColor, getSummaryRating } from '@/utils/ratingFiller'
export default {
  name: 'RatingBriefcaseDividends',
  data() {
    return {
      list: [],
      loading: false,
      briefcase: {},
      sumPrice: 0,
      headers: []
    }
  },
  computed: {
    fillUp: function() {
      return this.briefcase && this.briefcase.fill_up ? this.briefcase.fill_up : undefined
    }
  },
  watch: {
    strategyId: function() {
      this.fillHeaders()
    }
  },
  created() {
    this.fillHeaders()
    this.fetchList()
  },
  methods: {
    getRatingColor,
    fillHeaders() {
      this.headers = [
        { text: 'Комапания', value: 'company_name', class: 'briefcase-overall' },
        { text: 'Сектор', value: 'otrasl_name', class: 'briefcase-overall' },
        { text: 'Total rating', value: 'total_rating', class: 'briefcase-overall' },
        { text: 'Вес в портфеле', value: 'weight', class: 'briefcase-overall' },
        { text: 'Цена акции', value: 'close', class: 'briefcase-overall' },
        { text: 'Кол-во в лоте', value: 'lot_size', class: 'briefcase-overall' },
        { text: 'Стоимость лота', value: 'lot_price', class: 'briefcase-overall' },

        { text: 'Кол-во акций в портфеле', value: 'exist_count', class: 'briefcase-val-column' },
        { text: 'Общая стоимость', value: 'exist_price', class: 'briefcase-val-column' },
        { text: 'Доля в портфеле', value: 'exist_part', class: 'briefcase-val-column' },

        { text: 'Купить', value: 'price_to_buy', class: 'briefcase-column' },
        { text: 'Закупка лотов (план)', value: 'lots_to_buy_plan', class: 'briefcase-column' },
        { text: 'Закупка лотов (факт)', value: 'lots_to_buy_fact', class: 'briefcase-column' },
        { text: 'Стоимость закупки', value: 'fact_to_buy', class: 'briefcase-column' },
        { text: 'Итоговый портфель', value: 'total_briefcase', class: 'briefcase-column' },
        { text: 'Доля в портфеле', value: 'part_briefcase', class: 'briefcase-column' }
      ]
    },
    async fetchList() {
      this.loading = true
      const briefcases = await getData(endpoints.BRIEFCASE)
      this.briefcase = briefcases && briefcases.length > 0 ? briefcases[0] : null
      const fillUp = this.briefcase && this.briefcase['fill_up'] ? this.briefcase['fill_up'] : 0
      const [summaryRatings, compData] = await Promise.all([getSummaryRating(), getData(endpoints.RATINGS_BRIEFCASE)])
      let sumRating = 0
      this.sumPrice = 0
      const sumList = compData.map(c => {
        const rating = summaryRatings.find(r => r.company_id === c.company_id)
        const existPrice = c.exist_count ? c.exist_count * c.close : 0
        sumRating += rating && rating.ratingAverage ? rating.ratingAverage : 0
        this.sumPrice += existPrice || 0
        return Object.assign(c, {
          total_rating: rating.ratingAverage ? rating.ratingAverage : null,
          exist_price: existPrice || null
        })
      }).filter(c => c.total_rating).sort((a, b) => a.total_rating < b.total_rating ? 1 : a.total_rating > b.total_rating ? -1 : 0)

      const briefPrice = fillUp + this.sumPrice
      let sumExistBriefcase = 0
      let sumBriefcase = 0
      let sumFactToBuy = 0
      sumList.forEach(s => {
        const weight = s.total_rating ? Math.round(s.total_rating / sumRating * 10000, 2) / 100 : null
        const existPrice = s.exist_price ? s.exist_price : null
        const toBuy = Math.round(briefPrice * weight - (existPrice || 0) * 100) / 100
        const lotsPlanToBuy = Math.round(toBuy / s.lot_price * 100) / 100
        const factToBuy = s.lots_to_buy_fact && s.lot_price ? s.lots_to_buy_fact * s.lot_price : null
        const totalBriefcase = (factToBuy || 0) + (existPrice || 0)
        Object.assign(s, {
          weight: weight,
          price_to_buy: toBuy,
          lots_to_buy_plan: lotsPlanToBuy,
          lots_to_buy_fact: s.lots_to_buy_fact ? s.lots_to_buy_fact : null,
          fact_to_buy: factToBuy,
          total_briefcase: totalBriefcase
        })
        sumExistBriefcase += existPrice || 0
        sumBriefcase += totalBriefcase || 0
        sumFactToBuy += factToBuy || 0
      })

      sumList.forEach(s => {
        Object.assign(s, {
          exist_part: Math.round(s.exist_price / sumExistBriefcase * 10000) / 100,
          part_briefcase: Math.round(s.total_briefcase / sumBriefcase * 10000) / 100
        })
      })
      sumList.push({
        weight: 100,
        exist_price: this.sumPrice,
        fact_to_buy: sumFactToBuy,
        total_briefcase: sumBriefcase,
        exist_part: 100
      })
      this.list = sumList
      this.loading = false
    },
    changeFillUp(val) {
      putData(endpoints.BRIEFCASE, { id: this.briefcase.id, fill_up: val }).then(() => {
        this.fetchList()
      })
    },
    saveRatingBriefcaseValue(item) {
      if (item.lots_to_buy_fact && item.lots_to_buy_fact_id) {
        putData(endpoints.RATINGS_BRIEFCASE, item, false)
          .then(() => {
            this.fetchList()
            console.log('Updated')
          })
      } else
      if (!item.lots_to_buy_fact) {
        deleteData(endpoints.RATINGS_BRIEFCASE, { id: item.lots_to_buy_fact_id })
          .then(() => {
            this.fetchList()
            console.log('Deleted')
          })
      } else {
        postData(endpoints.RATINGS_BRIEFCASE, item, false)
          .then(() => {
            this.fetchList()
            console.log('Added')
          })
      }
    }
  }
}
</script>

<style>
.briefcase-val-column {
  background-color: #d1d5ef;
}
.briefcase-column {
  background-color: #d2eec6;
}
.briefcase-main-column {
  background-color: #eee4c6;
}
.briefcase-overall {
  font-weight: bold;
  background-color: #eee4c6;
  color: #0d47a1;
}
</style>

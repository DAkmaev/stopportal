<template>
  <div>
    <v-container fluid>
      <v-row justify="space-between">
        <v-col cols="3">
          <company-select
            :company="company"
            :strategy-ids="[2]"
            @company-changed="updateSelectedCompany"
          />
        </v-col>
        <v-col cols="3">
          <company-select
            :company="companyToAdd"
            :not-strategy-ids="[2]"
            label="Добавить компанию"
            @company-changed="addCompany"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col offset="1" cols="10">
        <!--<apexchart type="candlestick" :options="chartOptions" :series="series" />-->
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            :items="filteredList"
            :items-per-page="50"
            :headers="headers"
            item-key="name"
            :single-expand="singleExpand"
            :expanded.sync="expanded"
            show-expand
            fixed-header
            height="800px"
            :disable-pagination="false"
            :hide-default-footer="true"
            dense
            @click:row="handleCollapse"
          >
            <template v-slot:item.price_diff_perc="{ item }">
              <span>{{ ![null, undefined].includes(item.price_diff_perc) ? (Math.round(item.price_diff_perc * 100, 2) / 100) + '%' : '' }}</span>
            </template>
            <template v-slot:item.resistance="{ item }">
              <div :class="item.price >= item.resistance ? 'green lighten-4 rounded': ''" align="center">
                {{ item.resistance }}
              </div>
            </template>
            <template v-slot:item.support="{ item }">
              <div :class="item.price <= item.support ? 'red lighten-4 rounded': ''" align="center">
                {{ item.support }}
              </div>
            </template>
            <template v-slot:item.signal_buy="{ item }">
              <div :class="item.price >= item.signal_buy ? 'green lighten-4 rounded': ''" align="center">
                {{ item.signal_buy }}
              </div>
            </template>
            <template v-slot:item.risk_level="{ item }">
              <div align="center">
                {{ item.risk_level }}
              </div>
            </template>
            <template v-slot:expanded-item="{ item }">
              <td :colspan="headers.length">
                <mih-details
                  :strategy="item"
                  @mih-item-refresh="fetchList"
                  @mih-item-update="saveMihData(item)"
                  @mih-item-default-update="saveMihDataLinks"
                />
              </td>
            </template>
            <template v-slot:item.important="{ item }">
              <v-btn
                icon
                :color="item.important ? 'light-blue lighten-3' : 'grey lighten-3'"
                @click="changeImportant(item)"
              >
                <v-icon>mdi-star</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import MihDetails from '@/components/strategies/MihDetails'
import { getData, putData, endpoints } from '@/api/invmos-back'
import CompanySelect from '@/components/companies/CompanySelect'
export default {
  name: 'MihStrategy',
  components: { MihDetails, CompanySelect },
  data() {
    return {
      list: [],
      company: undefined,
      companyToAdd: undefined,
      headers: [
        { text: '', value: 'important' },
        { text: 'Тикер', value: 'tiker' },
        { text: 'Компания', value: 'name' },
        { text: 'Цена закрытия', value: 'price', align: 'center' },
        { text: '% изменения цены', value: 'price_diff_perc', align: 'center' },
        { text: 'Сопротивление', value: 'resistance', align: 'center' },
        { text: 'Поддержка', value: 'support', align: 'center' },
        { text: 'Покупать при цене', value: 'signal_buy', align: 'center' },
        { text: 'Стоп-лосс', value: 'risk_level', align: 'center' },
        { text: 'Коментарий', value: 'decision' },
        { text: '', value: 'data-table-expand' }
      ],
      expanded: [],
      singleExpand: true
    }
  },
  computed: {
    filteredList: function() {
      return this.company ? this.list.filter(l => l.company_id === this.company) : this.list
    }
  },
  watch: {},
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      this.list = await getData(endpoints.STRATEGIES_MIH)
    },
    async fetchCandleData() {
      const prices = await getData(endpoints.PRICES, { companyId: this.company })
      const getData = (prices) => {
        const getWeek = (date) => {
          const onejan = new Date(date.getFullYear(), 0, 1)
          return Math.ceil((((date - onejan) / 86400000) + onejan.getDay() + 1) / 7)
        }
        if (this.grouping === 'day') { return prices }

        const dates = []
        for (let i = 1; i < prices.length; i++) {
          new Date().getDay()
          const curVal = this.grouping === 'month' ? prices[i].date.getMonth() : getWeek(prices[i].date)
          const prevVal = this.grouping === 'month' ? prices[i - 1].date.getMonth() : getWeek(prices[i - 1].date)
          if (curVal !== prevVal) { dates.push(prices[i - 1]) } else
          if (i === prices.length - 1) { dates.push(prices[i]) }
        }
        return dates
      }
      const data = getData(prices).map(p => {
        return ({
          x: p.date,
          y: [p.open, p.high, p.low, p.close]
        })
      })

      this.series = [{
        name: 'candle',
        data: data
      }]
    },
    saveMihData(item) {
      putData(endpoints.STRATEGIES_MIH, item)
        .then(() => {
          this.fetchList()
          console.log('Updated')
        })
    },
    saveMihDataLinks(id, value, field) {
      const item = this.list.find(l => l.id === id)
      item[field] = value
      return this.saveMihData(item)
    },
    changeImportant(item) {
      item.important = !item.important
      return this.saveMihData(item)
    },
    updateSelectedCompany(val) {
      this.company = val ? val.id : undefined
    },
    addCompany(val) {
      val.strategies_ids.push(2)
      putData(endpoints.COMPANIES_STRATEGIES, val, false).then(() => {
        this.companyToAdd = null
        this.fetchList()
      })
    },
    handleCollapse(rows) {
      this.expanded = this.expanded.length > 0 ? [] : [rows]
    }
  }
}
</script>

<style scoped>

</style>


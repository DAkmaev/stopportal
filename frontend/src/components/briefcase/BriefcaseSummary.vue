<template>
  <div>
    <v-container fluid>
      <v-row class="justify">
        <v-col cols="2">
          <v-menu
            ref="menuFrom"
            v-model="dateFromMenu"
            :close-on-content-click="false"
            :return-value.sync="dateFrom"
            transition="scale-transition"
            offset-y
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                v-model="dateFrom"
                label="Дата от"
                prepend-icon="mdi-calendar"
                readonly
                clearable
                @click:clear="clearDate"
                v-on="on"
              />
            </template>
            <v-date-picker
              v-model="dateFrom"
              no-title
              scrollable
              @change="fetchList"
            >
              <v-spacer />
              <v-btn
                text
                color="primary"
                @click="dateFromMenu = false"
              >Отмена</v-btn>
              <v-btn
                text
                color="primary"
                @click="$refs.menuFrom.save(dateFrom)"
              >OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-col>
        <v-col cols="2">
          <v-menu
            ref="menuTo"
            v-model="dateToMenu"
            :close-on-content-click="false"
            :return-value.sync="dateTo"
            transition="scale-transition"
            offset-y
            min-width="290px"
          >
            <template v-slot:activator="{ on }">
              <v-text-field
                v-model="dateTo"
                label="Дата до"
                prepend-icon="mdi-calendar"
                readonly
                clearable
                @click:clear="clearDate"
                v-on="on"
              />
            </template>
            <v-date-picker
              v-model="dateTo"
              no-title
              scrollable
              @change="fetchList"
            >
              <v-spacer />
              <v-btn
                text
                color="primary"
                @click="dateToMenu = false"
              >Отмена</v-btn>
              <v-btn
                text
                color="primary"
                @click="$refs.menuTo.save(dateTo)"
              >OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            dense
            :items="list"
            :headers="headers"
            :disable-pagination="false"
            :hide-default-footer="true"
          >
            <template v-slot:item.part_name="{ item }">
              {{ parts[item.part_name].name }}
            </template>
            <template v-slot:item.type_document="{ item }">
              {{ documentTypes[item.type_document].name }}
            </template>
            <template v-slot:item.brief_part_perc="{ item }">
              <span v-if="item.brief_part_perc">{{ item.brief_part_perc }}%</span>
            </template>
            <template v-slot:item.price_start="{ item }">
              <span>{{ item.price_start | formatPrice(item.currency) }}</span>
            </template>
            <template v-slot:item.price_end="{ item }">
              <span>{{ item.price_end | formatPrice(item.currency) }}</span>
            </template>
            <template v-slot:item.dohodnost_perc="{ item }">
              <span v-if="item.dohodnost_perc">{{ item.dohodnost_perc }}%</span>
            </template>
            <template v-slot:item.count="{ item }">
              <v-edit-dialog
                :return-value.sync="item.count"
                @save="saveCompanyBriefcase(item)"
              >
                {{ item.count }}
                <template v-slot:input>
                  <v-text-field
                    v-model="item.count"
                    label="Изменить"
                    single-line
                  />
                </template>
              </v-edit-dialog>
            </template>
            <template v-slot:item.dividends="{ item }">
              <v-edit-dialog
                :return-value.sync="item.dividends"
                @save="saveCompanyBriefcase(item)"
              >
                {{ item.dividends }}
                <template v-slot:input>
                  <v-text-field
                    v-model="item.dividends"
                    label="Изменить"
                    single-line
                  />
                </template>
              </v-edit-dialog>
            </template>
            <template v-slot:item.withdrawal="{ item }">
              <v-edit-dialog
                :return-value.sync="item.withdrawal"
                @save="saveCompanyBriefcase(item)"
              >
                {{ item.withdrawal }}
                <template v-slot:input>
                  <v-text-field
                    v-model="item.withdrawal"
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
import { getData, getStrategies, endpoints } from '@/api/invmos-back'
import { mapGetters } from 'vuex'

export default {
  name: 'BriefcaseSummary',
  filters: {
    formatPrice: function(price, currency) {
      if (!price) { return '' }
      let cur = ''
      switch (currency) {
        case 'RUB': cur = '₽'
          break
        case 'USD': cur = '$'
          break
        case 'EUR': cur = '€'
          break
      }
      return `${price} ${cur}`
    }
  },
  data() {
    return {
      parts: {
        moderate: { id: 'moderate', name: 'Умеренная' },
        conservative: { id: 'conservative', name: 'Консервативная' },
        aggressive: { id: 'aggressive', name: 'Агрессивная' }
      },
      documentTypes: {
        stock_rf: { id: 'stock_rf', name: 'Акции РФ' },
        stock_usa: { id: 'stock_usa', name: 'Акции США' },
        etf: { id: 'etf', name: 'ETF' }
      },
      strategies: [],
      companies: [],
      list: [],
      headers: [
        { text: 'Компания', value: 'company.name', class: 'briefcase-val-column' },
        { text: 'Тикер', value: 'company.tiker', class: 'briefcase-val-column' },
        { text: 'Сектор', value: 'otrasl_name', class: 'briefcase-val-column' },
        /*        { text: 'Часть портфеля', value: 'part_name', class: 'briefcase-val-column' },
        { text: 'Тип документа', value: 'type_document', class: 'briefcase-val-column' },*/
        { text: 'Стратегия', value: 'strategy_name', class: 'briefcase-val-column' },
        { text: 'Кол-во', value: 'count', class: 'briefcase-overall' },
        { text: 'Ликвид. цена НП', value: 'price_start', class: 'briefcase-main-column' },
        { text: 'Стоимость ЦБ НП', value: 'cb_start', class: 'briefcase-main-column' },
        { text: 'Ликвид. цена КП', value: 'price_end', class: 'briefcase-main-column' },
        { text: 'Стоимость ЦБ КП', value: 'cb_end', class: 'briefcase-main-column' },
        { text: 'Доля в портфеле', value: 'brief_part_perc', class: 'briefcase-val-column' },
        { text: 'Дивиденды / купоны', value: 'dividends', class: 'briefcase-overall' },
        { text: 'Вывод', value: 'withdrawal', class: 'briefcase-overall' },
        { text: 'Доходность', value: 'dohodnost', class: 'briefcase-column' },
        { text: 'Доходность %', value: 'dohodnost_perc', class: 'briefcase-column' }
      ],
      dialog: false,
      dateFrom: undefined,
      dateTo: undefined,
      dateFromMenu: false,
      dateToMenu: false,
      temp: {
        company: { id: undefined },
        strategy: { id: undefined },
        part_name: undefined,
        type_document: undefined,
        dividends: undefined,
        withdrawal: undefined,
        count: undefined
      }
    }
  },
  computed: {
    ...mapGetters(['token'])
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      const [strategies, companies] = await Promise.all([
        getStrategies(this.token),
        getData(endpoints.COMPANIES, { fields: 'c.id,c.name' }, this.token)
      ])
      this.strategies = strategies
      this.companies = companies

      let sumCBstart = 0
      // let sumCBend = 0
      // let sumDohodnost = 0
      // let sumDividends = 0
      const data = []
      data.forEach(d => {
        const dohodnost = Math.round(((d.dividends || 0) + (d.cb_end || 0) - (d.cb_start || 0)) * 100, 2) / 100
        const dohodnost_perc = dohodnost ? Math.round(dohodnost / d.cb_start * 10000, 2) / 100 : null
        sumCBstart += d.cb_start || 0
        // sumCBend += d.cb_end || 0
        // sumDohodnost += dohodnost
        // sumDividends += d.dividends || 0
        Object.assign(d, {
          dohodnost: dohodnost,
          dohodnost_perc: dohodnost_perc
        })
      })

      data.forEach(d => {
        const briefPartPerc = d.cb_start && sumCBstart ? Math.round(d.cb_start / sumCBstart * 10000, 2) / 100 : null
        Object.assign(d, {
          brief_part_perc: briefPartPerc
        })
      })

      this.list = data
    },
    clearDate() {
      this.$nextTick(() => {
        this.$nextTick(() => {
          this.fetchList()
        })
      })
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
  background-color: #e0c6ee;
  color: #0d47a1;
}
</style>

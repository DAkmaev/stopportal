<template>
  <div>
    <v-container fluid>
      <v-row class="justify">
        <v-col>
          <v-item-group>
            <v-btn small dark fab color="primary" class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          </v-item-group>
        </v-col>
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
      <v-dialog v-if="dialog" v-model="dialog" :eager="true" scrollable max-width="980px">
        <v-card>
          <v-card-title>
            Добавление акций
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-form ref="addForm">
                <v-row>
                  <v-col cols="12" sm="6" md="6">
                    <v-autocomplete
                      v-model="temp.company.id"
                      no-data-text="Нет данных"
                      label="Выберите компанию"
                      :items="companies"
                      item-text="name"
                      item-value="id"
                      clearable
                    />
                  </v-col>

                </v-row>
                <v-row>
                  <v-col cols="8" sm="4" md="4">
                    <v-autocomplete
                      v-model="temp.strategy.id"
                      no-data-text="Нет данных"
                      label="Выберите стратегии"
                      :items="strategies"
                      item-text="name"
                      item-value="id"
                      clearable
                    />
                  </v-col>
                  <v-col cols="8" sm="4" md="4">
                    <v-autocomplete
                      v-model="temp.part_name"
                      no-data-text="Нет данных"
                      label="Выберите часть портфеля"
                      :items="Object.values(parts)"
                      item-text="name"
                      item-value="id"
                      clearable
                    />
                  </v-col>
                  <v-col cols="8" sm="4" md="4">
                    <v-autocomplete
                      v-model="temp.type_document"
                      no-data-text="Нет данных"
                      label="Выберите тип документа"
                      :items="Object.values(documentTypes)"
                      item-text="name"
                      item-value="id"
                      clearable
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6" sm="3" md="3">
                    <v-text-field
                      v-model="temp.count"
                      label="Количество акций"
                      required
                    />
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-text-field
                      v-model="temp.dividends"
                      label="Дивиденды / купоны"
                      required
                    />
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-text-field
                      v-model="temp.withdrawal"
                      label="Вывод"
                      required
                    />
                  </v-col>
                </v-row>
                <v-card-actions>
                  <v-spacer />
                  <v-btn text @click="dialog = false">Отмена</v-btn>
                  <v-btn text color="primary" @click="addData">Сохранить</v-btn>
                </v-card-actions>
              </v-form>
            </v-container>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { getData, putData, getStrategies, endpoints, postData, deleteData } from '@/api/invmos-back'

// todo: переделать когда будет реализовано несколько портфелей
const BRIEFCASE_ID = 1
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
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      const [data, strategies, companies] = await Promise.all([
        getData(`${endpoints.BRIEFCASE}/${BRIEFCASE_ID}/items/`, { dateFrom: this.dateFrom, dateTo: this.dateTo }),
        getStrategies(),
        getData(endpoints.COMPANIES, { fields: 'c.id,c.name' })
      ])
      this.strategies = strategies
      this.companies = companies

      let sumCBstart = 0
      // let sumCBend = 0
      // let sumDohodnost = 0
      // let sumDividends = 0
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
    },
    saveCompanyBriefcase(item) {
      if (item.count) {
        putData(`${endpoints.BRIEFCASE_ITEMS}/${item.id}`, item, false)
          .then(() => {
            this.fetchList()
            console.log('Updated')
          })
      } else {
        deleteData(`${endpoints.BRIEFCASE_ITEMS}/${item.id}`).then(() => {
          this.fetchList()
          console.log('Deleted')
        })
      }
    },
    handleAdd() {
      this.resetTemp()
      this.dialog = true
    },
    addData() {
      const temp = { ...this.temp }
      if (!temp.strategy.id) {
        temp.strategy = null
      }

      postData(`${endpoints.BRIEFCASE}/${BRIEFCASE_ID}/items/`, temp, false)
        .then(() => {
          this.dialog = false
          this.fetchList()
          console.log('Added')
        })
    },
    resetTemp() {
      this.temp = {
        company: { id: undefined },
        strategy: { id: undefined },
        part_name: undefined,
        type_document: undefined,
        dividends: undefined,
        withdrawal: undefined,
        count: undefined
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
  background-color: #e0c6ee;
  color: #0d47a1;
}
</style>

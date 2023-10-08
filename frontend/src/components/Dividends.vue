<template>
  <div>
    <v-container fluid>
      <v-row justify="end">
        <v-col class="ma-4">
          <v-btn small dark fab color="primary" class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
        </v-col>
        <v-col>
          <v-autocomplete
            v-model="company"
            no-data-text="Нет данных"
            label="Выберите компанию"
            :items="companies"
            item-text="name"
            item-value="id"
            clearable
            @change="fetchList"
          />
        </v-col>
        <v-col>
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
        <v-col>
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
        <v-col class="ma-4" align="right">
          <v-btn
            fab
            small
            color="primary"
            :loading="syncing"
            @click="syncDividends"
          ><v-icon>mdi-cached</v-icon></v-btn>
        </v-col>
      </v-row>
      <v-data-table
        :items="list"
        :items-per-page="50"
        :headers="headers"
        item-key="name"
        dense
      >
        <template v-slot:item.company_id="{ item }">
          <span>{{ companyName(item.company_id) }}</span>
        </template>
        <template v-slot:item.period="{ item }">
          <span>{{ periodName(item) }}</span>
        </template>
        <template v-slot:item.date_fixing="{ item }">
          <span>{{
            new Date(item.date_fixing).toLocaleString('sv').substr(0, 10)
          }}</span>
        </template>
        <template v-slot:item.date_can_buy="{ item }">
          <span>{{
            new Date(item.date_can_buy).toLocaleString('sv').substr(0, 10)
          }}</span>
        </template>
        <template v-slot:item.profit="{ item }">
          <span>{{ Math.round(item.profit * 100, 2) / 100 }}%</span>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="handleEdit(item)">
            mdi-pencil
          </v-icon>
          <v-icon small @click="handleDelete(item)">
            mdi-delete
          </v-icon>
        </template>
      </v-data-table>
      <v-row justify="center">
        <v-dialog v-model="dialog" persistent max-width="800px">
          <v-card>
            <v-card-title>
              {{ dialogModes[dialogMode] }}
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col>
                    <v-autocomplete
                      v-model="temp.company_id"
                      no-data-text="Нет данных"
                      label="Выберите компанию"
                      :items="companies"
                      item-text="name"
                      item-value="id"
                      :rules="rules.companyRules"
                      clearable
                      required
                    />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col sm="6">
                    <v-select v-model="temp.period_months" :items="periodMonths" label="Месяцев за период" />
                  </v-col>
                  <v-col sm="6">
                    <v-select v-model="temp.period_year" :items="periodYears" label="Год периода" />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col sm="6">
                    <v-menu
                      v-model="temp.date_fixing_menu"
                      :rules="rules.dateFixingRules"
                      :close-on-content-click="false"
                      :nudge-right="40"
                      transition="scale-transition"
                      offset-y
                      min-width="290px"
                    >
                      <template v-slot:activator="{ on }">
                        <v-text-field
                          v-model="temp.date_fixing"
                          label="Дата закрытия реестра"
                          prepend-icon="mdi-calendar"
                          readonly
                          v-on="on"
                        />
                      </template>
                      <v-date-picker
                        v-model="temp.date_fixing"
                        @input="temp.date_fixing_menu = false"
                      />
                    </v-menu>
                  </v-col>
                  <v-col sm="6">
                    <v-menu
                      v-model="temp.date_can_buy_menu"
                      :close-on-content-click="false"
                      :nudge-right="40"
                      transition="scale-transition"
                      offset-y
                      min-width="290px"
                    >
                      <template v-slot:activator="{ on }">
                        <v-text-field
                          v-model="temp.date_can_buy"
                          label="Последний день покупки"
                          prepend-icon="mdi-calendar"
                          readonly
                          v-on="on"
                        />
                      </template>
                      <v-date-picker
                        v-model="temp.date_can_buy"
                        @input="temp.date_can_buy_menu = false"
                      />
                    </v-menu>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col sm="4">
                    <v-text-field
                      v-model="temp.last_price"
                      label="Цена акции на закрытие"
                      required
                    />
                  </v-col>
                  <v-col sm="4">
                    <v-text-field
                      v-model="temp.payment"
                      label="Размер дивиденда"
                    />
                  </v-col>
                  <v-col sm="4">
                    <v-text-field
                      v-model="temp.profit"
                      label="Доходность"
                      disabled
                    />
                  </v-col>
                </v-row>
                <v-card-actions>
                  <v-spacer />
                  <v-btn text color="primary" @click="handleCancel">Отмена</v-btn>
                  <v-btn
                    text
                    :disabled="!valid"
                    @click="saveItem"
                  >Сохранить</v-btn>
                </v-card-actions>
              </v-container>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-row>
      <!--<v-btn bottom color="pink" dark fab fixed right @click="handleAdd">
        <v-icon>mdi-plus</v-icon>
      </v-btn>-->
    </v-container>
  </div>
</template>

<script>
import { getData, postData, putData, deleteData, endpoints } from '@/api/invmos-back'
import { getDividends } from '@/api/open-broker'
export default {
  name: 'Dividends',
  props: {
    fromDefault: {
      type: Number,
      default: 10 * 31556926000 // 10 years
    }
  },
  data() {
    return {
      dialog: false,
      valid: true,
      dialogMode: '',
      dialogModes: {
        add: 'Добавить дивиденды',
        edit: 'Редактировать дивиденды'
      },
      periodMonths: [3, 6, 9, 12],
      periodYears: [...Array(15).keys()].map(i => 2022 - i),
      syncing: false,
      companies: [],
      company: undefined,
      list: [],
      temp: {
        id: undefined,
        company_id: '',
        period_months: undefined,
        period_year: undefined,
        date_fixing: undefined,
        date_fixing_menu: false,
        date_can_buy: undefined,
        date_can_buy_menu: false,
        payment: undefined,
        last_price: undefined,
        profit: undefined
      },
      dateFrom: undefined,
      dateTo: undefined,
      dateFromMenu: false,
      dateToMenu: false,
      headers: [
        {
          text: 'Компания',
          align: 'start',
          value: 'company_id'
        },
        { text: 'Период', value: 'period' },
        { text: 'Цена акции на закрытии', value: 'last_price' },
        { text: 'Дата закрытия реестра', value: 'date_fixing' },
        { text: 'Последний день покупки', value: 'date_can_buy' },
        { text: 'Размер дивиденда', value: 'payment' },
        { text: 'Доходность', value: 'profit' },
        { text: 'Действия', value: 'actions', sortable: false }
      ],
      rules: {
        dateFixingRules: [v => !!v || 'Дата фиксации обязательна'],
        companyRules: [
          v => !!v || 'Выберите компанию',
          v => (v && !v.isNan) || 'Компания должна быть задана'
        ]
      }
    }
  },
  computed: {
    tiker() {
      return this.company !== undefined
        ? this.companies.find(c => c.id === this.company).tiker
        : ''
    },
    companiesKeyMap() {
      return this.companies.reduce(function(map, obj) {
        map[obj.id] = obj
        return map
      }, {})
    },
    profit() {
      return !!this.temp.payment && !!this.temp.last_price
        ? Math.round((this.temp.payment / this.temp.last_price) * 10000, 2) /
            100
        : 0
    }
  },
  watch: {
    profit() {
      this.temp.profit = this.profit ? this.profit : ''
    }
  },
  created() {},
  mounted() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      getData(endpoints.COMPANIES, { fields: 'c.id,c.name,c.tiker' }).then(data => {
        this.companies = data
        getData(endpoints.DIVIDENDS, {
          dateFrom: this.dateFrom,
          dateTo: this.dateTo,
          companyId: this.company
        }).then(
          dividends => {
            this.list = dividends
          }
        )
      })
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        company_id: '',
        period_months: undefined,
        period_year: undefined,
        date_fixing: undefined,
        date_can_buy: undefined,
        date_fixing_menu: false,
        date_can_buy_menu: false,
        payment: undefined,
        last_price: undefined,
        profit: undefined
      }
    },
    handleAdd() {
      this.resetTemp()
      this.dialogMode = 'add'
      this.dialog = true
    },
    saveItem() {
      if (this.dialogMode === 'add') this.addItem()
      else this.editItem()
    },
    addItem() {
      postData(endpoints.DIVIDENDS, [this.temp], false)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(item) {
      // this.temp = this.list.indexOf(item)
      this.dialogMode = 'edit'
      this.temp = Object.assign({}, item)
      this.temp.date_fixing = new Date(item.date_fixing)
        .toLocaleString('sv')
        .substr(0, 10)
      this.temp.date_can_buy = new Date(item.date_can_buy)
        .toLocaleString('sv')
        .substr(0, 10)
      this.dialog = true
    },
    editItem() {
      putData(endpoints.DIVIDENDS, this.temp)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    async syncDividends() {
      this.syncing = true
      const lastDate = await getData(endpoints.SYNC_LAST, { id: 2, fromDefault: this.fromDefault }, false)
      const companies = await getData(endpoints.COMPANIES)
      await Promise.all(
        companies.map(async c => {
          return this.saveDividendsData(c.tiker, lastDate, '', c.id)
        })
      ).catch(err => {
        console.error(err.message)
        this.syncing = false
      })
      this.fetchList()
      this.syncing = false
    },
    async saveDividendsData(tiker, dateFrom, dateTo, companyId) {
      const dividendsData = await getDividends(tiker, dateFrom, dateTo)
      return postData('dividends/data', dividendsData, false, { companyId: companyId })
    },
    companyName(id) {
      return this.companiesKeyMap[id] !== undefined
        ? this.companiesKeyMap[id].name
        : ''
    },
    periodName(item) {
      const monthsPart = item.period_months ? `${item.period_months} месяцев ` : ''
      const yearPart = item.period_year ? item.period_year : ''
      return `${monthsPart}${yearPart}`
    },
    handleDelete(item) {
      confirm('Вы точно хотите удалить?') &&
        deleteData(endpoints.DIVIDENDS, { id: item.id }).then(() => {
          this.active = []
          this.fetchList()
          console.log(`Deleted`)
        })
    }
  }
}
</script>

<style scoped></style>

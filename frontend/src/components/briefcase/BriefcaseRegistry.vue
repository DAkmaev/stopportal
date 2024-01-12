<template>
  <div>
    <v-container fluid>
      <v-row class="justify">
        <v-col>
          <v-item-group>
            <v-btn small dark fab color="primary" class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
            <v-btn v-show="hasSelected" color="green" dark fab small class="ms-2" @click="handleEdit(selectedItem.id)"><v-icon>mdi-pencil</v-icon></v-btn>
            <v-btn v-show="hasSelected" color="red" dark fab small class="ms-2" @click="handleDelete(selectedItem.id)"><v-icon>mdi-delete</v-icon></v-btn>
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
            v-model="selected"
            dense
            :items="list"
            :headers="headers"
            :disable-pagination="false"
            :hide-default-footer="true"
            show-select
            single-select
          >
            <template v-slot:item.strategy="{ item }">
              {{ item.strategy ? item.strategy.name : '' }}
            </template>
            <template v-slot:item.operation="{ item }">
              {{ operations[item.operation].name }}
            </template>
            <template v-slot:item.price="{ item }">
              <span>{{ item.price | formatPrice(item.currency) }}</span>
            </template>
            <template v-slot:item.created_date="{ item }">
              <span>{{ new Date(item.created_date).toLocaleDateString() }}</span>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-dialog v-if="dialog" v-model="dialog" :eager="true" scrollable max-width="980px">
        <v-card>
          <v-card-title>
            {{ dialogModes[dialogMode] }}
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-form ref="addForm" v-model="valid" fast-fail>
                <v-row>
                  <v-col cols="12" sm="6" md="6">
                    <v-autocomplete
                      v-model="temp.company.id"
                      no-data-text="Нет данных"
                      label="Выберите компанию *"
                      :rules="rules.companyRules"
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
                      v-model="temp.operation"
                      no-data-text="Нет данных"
                      label="Выберите операцию *"
                      :items="Object.values(operations)"
                      :rules="rules.operationRules"
                      item-text="name"
                      item-value="id"
                      clearable
                    />
                  </v-col>
                  <v-col cols="8" sm="4" md="4">
                    <v-autocomplete
                      v-model="temp.currency"
                      no-data-text="Нет данных"
                      label="Выберите валюту *"
                      :items="Object.values(currencies)"
                      :rules="rules.currencyRules"
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
                    />
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-text-field
                      v-model="temp.amount"
                      label="Сумма *"
                      :rules="rules.amountRules"
                      required
                    />
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-text-field
                      v-model="temp.price"
                      label="Цена"
                    />
                  </v-col>
                </v-row>
                <v-card-actions>
                  <v-spacer />
                  <v-btn text @click="dialog = false">Отмена</v-btn>
                  <v-btn text color="primary" :disabled="!valid" @click="saveItem">Сохранить</v-btn>
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
  name: 'BriefcaseRegistry',
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
      operations: {
        BUY: { id: 'BUY', name: 'Покупка' },
        SELL: { id: 'SELL', name: 'Продажа' },
        DIVIDENDS: { id: 'DIVIDENDS', name: 'Дивиденды' }
      },
      currencies: {
        RUB: { id: 'RUB', name: '₽' },
        USD: { id: 'USD', name: '$' },
        EUR: { id: 'EUR', name: '€' }
      },
      strategies: [],
      companies: [],
      list: [],
      headers: [
        { text: 'Компания', value: 'company.name' },
        { text: 'Тикер', value: 'company.tiker' },
        { text: 'Дата', value: 'company.created_date' },
        { text: 'Стратегия', value: 'strategy' },
        { text: 'Дата', value: 'created_date' },
        { text: 'Кол-во', value: 'count' },
        { text: 'Сумма', value: 'amount' },
        { text: 'Цена', value: 'price' },
        { text: 'Операция', value: 'operation' },
        { text: 'Валюта', value: 'currency' }
      ],
      dialog: false,
      dateFrom: undefined,
      dateTo: undefined,
      dateFromMenu: false,
      dateToMenu: false,
      temp: {
        company: { id: undefined },
        strategy: { id: undefined },
        amount: undefined,
        count: undefined,
        price: undefined,
        created_date: undefined,
        currency: undefined,
        operation: undefined
      },
      selected: [],
      dialogMode: '',
      dialogModes: {
        add: 'Добавить запись',
        edit: 'Редактировать запись'
      },
      rules: {
        companyRules: [
          v => !!v || 'Компания обязательна',
          v => Number.isInteger(v) || 'не правильный тип ID'
        ],
        operationRules: [
          v => !!v || 'Тип операции обязателен'
        ],
        amountRules: [
          v => !!v || 'Сумма обязательна'
        ],
        currencyRules: [
          v => !!v || 'Валюта обязательна'
        ]
      },
      valid: false
    }
  },
  computed: {
    selectedItem() {
      return this.selected && this.selected.length > 0 ? this.selected[0] : null
    },
    hasSelected() {
      return this.selectedItem !== null
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      const [data, strategies, companies] = await Promise.all([
        getData(`${endpoints.BRIEFCASE}/${BRIEFCASE_ID}/registry/`, { dateFrom: this.dateFrom, dateTo: this.dateTo }),
        getStrategies(),
        getData(endpoints.COMPANIES, { fields: 'c.id,c.name' })
      ])
      this.strategies = strategies
      this.companies = companies
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
    saveItem() {
      if (this.dialogMode === 'add') this.addItem()
      else this.editItem()
    },
    handleAdd() {
      this.resetTemp()
      this.dialogMode = 'add'
      this.dialog = true
    },
    addItem() {
      const temp = { ...this.temp }
      temp.strategy = temp.strategy && temp.strategy.id ? temp.strategy : null
      temp.price = temp.price ? temp.price : null
      temp.count = temp.count ? temp.count : null

      postData(`${endpoints.BRIEFCASE}/${BRIEFCASE_ID}/registry/`, temp, false)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(id) {
      this.temp = this.list.find(l => l.id === id)
      this.temp.company = this.temp.company && this.temp.company.id ? this.temp.company : { 'id': undefined }
      this.temp.strategy = this.temp.strategy && this.temp.strategy.id ? this.temp.strategy : { 'id': undefined }
      this.dialogMode = 'edit'
      this.dialog = true
    },
    editItem() {
      const { id, ...data } = this.temp
      data.company = data.company && data.company.id ? data.company : null
      data.strategy = data.strategy && data.strategy.id ? data.strategy : null

      putData(`${endpoints.BRIEFCASE_REGISTRY}/${id}`, data, false)
        .then(() => {
          this.$nextTick(() => {
            this.fetchList()
            this.dialog = false
            this.selected = []
          })
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete(id) {
      confirm('Вы точно хотите удалить?') &&
      deleteData(`${endpoints.BRIEFCASE_REGISTRY}/${id}`)
        .then(() => {
          this.active = []
          this.selected = []
          this.$nextTick(() => {
            this.fetchList()
          })
          console.log(`Deleted ${this.list.find(item => item.id === id).name}`)
        })
    },
    resetTemp() {
      this.temp = {
        company: { id: undefined },
        strategy: { id: undefined },
        amount: undefined,
        count: undefined,
        price: undefined,
        created_date: undefined,
        currency: undefined,
        operation: undefined
      }
    }
  }
}
</script>

<style>
</style>

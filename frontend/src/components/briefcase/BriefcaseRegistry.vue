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
            :page.sync="page"
            :items-per-page="itemsPerPage"
            :hide-default-footer="false"
            :footer-props="footerProps"
            show-select
            single-select
            @page-count="pageCount = $event"
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
          <!--  <div class="text-center pt-2">-->
          <!--    <v-pagination-->
          <!--    v-model="page"-->
          <!--    :length="pageCount"-->
          <!--    />-->
          <!--    </div>-->
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
                  <v-col cols="12" sm="6" md="6">
                    <v-menu
                      ref="menuCreatedDate"
                      v-model="datePickerDialog"
                      :close-on-content-click="false"
                      :return-value.sync="temp.created_date"
                      transition="scale-transition"
                      offset-y
                      min-width="290px"
                    >
                      <template v-slot:activator="{ on }">
                        <v-text-field
                          v-model="temp.created_date"
                          label="Дата"
                          prepend-icon="mdi-calendar"
                          readonly
                          v-on="on"
                        />
                      </template>
                      <v-date-picker
                        v-model="temp.created_date"
                        no-title
                        scrollable
                      >
                        <v-spacer />
                        <v-btn
                          text
                          color="primary"
                          @click="datePickerDialog = false"
                        >Отмена</v-btn>
                        <v-btn
                          text
                          color="primary"
                          @click="$refs.menuCreatedDate.save(temp.created_date)"
                        >OK</v-btn>
                      </v-date-picker>
                    </v-menu>
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
                      v-model="temp.price"
                      label="Цена"
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
      briefcaseId: null,
      strategies: [],
      companies: [],
      list: [],
      headers: [
        { text: 'Дата', value: 'created_date' },
        { text: 'Тикер', value: 'company.tiker' },
        { text: 'Компания', value: 'company.name' },
        { text: 'Операция', value: 'operation' },
        { text: 'Кол-во', value: 'count' },
        { text: 'Цена', value: 'price' },
        { text: 'Сумма', value: 'amount' },
        { text: 'Валюта', value: 'currency' },
        { text: 'Стратегия', value: 'strategy' }
      ],
      dialog: false,
      dateFrom: undefined,
      dateTo: undefined,
      dateFromMenu: false,
      dateToMenu: false,
      datePickerDialog: false,
      temp: {
        company: { id: undefined },
        strategy: { id: undefined },
        amount: undefined,
        count: undefined,
        price: undefined,
        created_date: undefined,
        currency: 'RUB',
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
        ],
        createdDateRules: [
          v => !!v || 'Дата обязательна'
        ]
      },
      valid: false,
      page: 1,
      pageCount: 0,
      itemsPerPage: 200,
      footerProps: { 'items-per-page-options': [100, 200, 500, -1] }
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
  watch: {
    'temp.price': function(newVal, oldVal) {
      if (newVal && this.temp.count) {
        if (newVal !== oldVal) {
          this.temp.amount = newVal * this.temp.count
        }
      } else {
        if (!newVal && oldVal || newVal && !oldVal && !this.temp.count) {
          this.temp.amount = undefined
        }
      }
    },
    'temp.count': function(newVal, oldVal) {
      if (newVal && this.temp.price) {
        if (newVal !== oldVal) {
          this.temp.amount = newVal * this.temp.price
        }
      } else {
        if (!newVal && oldVal || newVal && !oldVal && !this.temp.price) {
          this.temp.amount = undefined
        }
      }
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      const briefcases = await getData(endpoints.BRIEFCASE, null)
      this.briefcaseId = briefcases[0].id
      const [data, strategies, companies] = await Promise.all([
        getData(`${endpoints.BRIEFCASE}/${this.briefcaseId}/registry/`, {
          date_from: this.dateFrom,
          date_to: this.dateTo
          // limit: this.itemsPerPage,
          // offset: (this.page - 1) * this.itemsPerPage
        }),
        getStrategies(this.token),
        getData(endpoints.COMPANIES, { fields: 'c.id,c.name', limit: 1000 })
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
    saveItem() {
      if (this.dialogMode === 'add') this.addItem()
      else this.editItem()
    },
    handleAdd() {
      this.resetTemp()
      this.temp.created_date = this.toLocalDateISOString(new Date().toISOString())
      this.dialogMode = 'add'
      this.dialog = true
    },
    addItem() {
      const temp = { ...this.temp }
      temp.strategy = temp.strategy && temp.strategy.id ? temp.strategy : null
      temp.price = temp.price ? temp.price : null
      temp.count = temp.count ? temp.count : null
      temp.created_date = this.toLocalISOString(temp.created_date)

      postData(`${endpoints.BRIEFCASE}/${this.briefcaseId}/registry/`, temp, null, this.token)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(id) {
      this.temp = { ...this.list.find(l => l.id === id) }
      this.temp.company = this.temp.company && this.temp.company.id ? this.temp.company : { 'id': undefined }
      this.temp.strategy = this.temp.strategy && this.temp.strategy.id ? this.temp.strategy : { 'id': undefined }
      this.temp.created_date = this.toLocalDateISOString(this.temp.created_date)
      this.dialogMode = 'edit'
      this.dialog = true
    },
    editItem() {
      const { id, ...data } = this.temp
      data.company = data.company && data.company.id ? data.company : null
      data.strategy = data.strategy && data.strategy.id ? data.strategy : null
      data.created_date = this.toLocalISOString(data.created_date)

      putData(`${endpoints.BRIEFCASE}/${this.briefcaseId}/registry/${id}`, data, null, this.token)
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
      deleteData(`${endpoints.BRIEFCASE}/${this.briefcaseId}/registry/${id}`, null, this.token)
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
        currency: 'RUB',
        operation: undefined
      }
    },
    toLocalISOString(dateStr) {
      const date = new Date(dateStr)
      return date ? new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString() : undefined
    },
    toLocalDateISOString(dateStr) {
      const dateTimeStr = this.toLocalISOString(dateStr)
      return dateTimeStr ? dateTimeStr.slice(0, 10) : undefined
    }
  }
}
</script>

<style>
</style>

<template>
  <div>
    <v-container fluid>
      <v-row class="justify">
        <v-col cols="3">
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
        <v-col align="right" offset="1">
          <v-text-field
            v-if="capitalization"
            class="centered-input"
            :value="prettyCapitalization"
            persistent-hint
            hint="Капитализация"
            readonly
          />
        </v-col>
        <v-col align="right">
          <v-btn
            v-if="tiker === ''"
            color="primary"
            :loading="syncing"
            @click="syncPrices"
          ><v-icon>mdi-cached</v-icon></v-btn>
          <v-btn
            v-else
            color="primary"
            :loading="syncing"
            @click="syncCompPrices"
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
        <template v-slot:item.date="{ item }">
          <span>{{ new Date(item.date).toLocaleString('sv').substr(0, 10) }}</span>
        </template>
        <template v-slot:item.close="{ item }">
          <span>{{ item.close | formatPrice(item.currency) }}</span>
        </template>
      </v-data-table>
    </v-container>
  </div>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'
import { prettyNumber } from '@/utils/prettifier'
import PriceSynchronizer from '@/utils/PriceSynchronizer'
export default {
  name: 'Prices',
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
  props: {
    fromDefault: {
      type: Number,
      default: 31556926000 // 1 year
    }
  },
  data() {
    return {
      priceSynchronizer: new PriceSynchronizer(),
      syncing: false,
      companies: [],
      company: undefined,
      list: [],
      dateFrom: new Date(Date.now() - this.fromDefault)
        .toLocaleString('sv')
        .substr(0, 10),
      dateTo: new Date().toLocaleString('sv').substr(0, 10),
      dateFromMenu: false,
      dateToMenu: false,
      headers: [
        {
          text: 'Компания',
          align: 'start',
          value: 'company_id'
        },
        { text: 'Дата', value: 'date' },
        { text: 'Цена закрытия', value: 'close' }
      ]
    }
  },
  computed: {
    tiker() {
      return this.company
        ? this.companies.find(c => c.id === this.company).tiker
        : ''
    },
    companiesKeyMap() {
      return this.companies.reduce(function(map, obj) {
        map[obj.id] = obj
        return map
      }, {})
    },
    capitalization() {
      if (this.company && this.list.length > 0) {
        const issueSize = this.companies.find(c => c.id === this.company).issue_size
        const cap = this.companies.find(c => c.id === this.company).capitalization
        return cap || (issueSize ? issueSize * this.list[0].price_close : null)
      } else { return null }
    },
    prettyCapitalization() {
      return this.capitalization ? prettyNumber(this.capitalization) : null
    }
  },
  created() {
    // this.syncCompPrices()
  },
  mounted() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      getData(endpoints.COMPANIES, { fields: 'c.id,c.name,c.tiker,c.currency,c.issue_size,c.capitalization' })
        .then(data => {
          this.companies = data
          getData(endpoints.PRICES, {
            dateFrom: this.dateFrom,
            dateTo: this.dateTo,
            companyId: this.company
          }).then(
            prices => {
              this.list = prices
            }
          )
        })
    },
    async syncCompPrices() {
      this.syncing = true
      await this.priceSynchronizer.sync([this.company])
      this.fetchList()
      this.syncing = false
    },
    async syncPrices() {
      this.syncing = true
      await this.priceSynchronizer.sync()
      this.fetchList()
      this.syncing = false
    },
    companyName(id) {
      return this.companiesKeyMap[id] !== undefined
        ? this.companiesKeyMap[id].name
        : ''
    }
  }
}
</script>

<style>
  .centered-input input {
    text-align: center
  }
  .centered-input .v-messages__message {
    text-align: center
  }
</style>

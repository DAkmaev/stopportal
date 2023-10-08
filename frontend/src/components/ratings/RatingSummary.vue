<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col>
          <v-data-table
            dense
            :disable-pagination="true"
            :items="list"
            :headers="headers"
            :loading="loading"
          ><template v-slot:item.ratingAverage="{ item }">
            <v-chip :color="getColor(item.ratingAverage, 1)" small>{{ item.ratingAverage }}</v-chip>
          </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
    <v-snackbar
      v-model="snackbar.enable"
      :color="snackbar.color"
      top
      right
      :timeout="6000"
    >
      {{ snackbar.text }}
      <v-btn
        dark
        text
        @click="snackbar.enable = false"
      >
        X
      </v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { prettyNumber } from '@/utils/prettifier'
import { getRatingColor, getSummaryRating } from '@/utils/ratingFiller'

export default {
  name: 'RatingSummary',
  props: {},
  data() {
    return {
      list: [],
      loading: false,
      headers: [
        { text: 'Комапания', value: 'name', class: 'rating-main-column' },
        { text: 'Отрасль', value: 'otrasl', class: 'rating-main-column' },
        { text: 'Рейтинг стабильности дивидендов', value: 'dividendsVal', align: 'center', class: 'rating-val-column' },
        { text: 'Див. доходность', value: 'dividendsDohodnostVal', align: 'center', class: 'rating-val-column' },
        { text: 'Чистый долг', value: 'debtVal', align: 'center', class: 'rating-val-column' },
        { text: 'Свободный денежный поток', value: 'freeMoneyFlowVal', align: 'center', class: 'rating-val-column' },
        { text: 'Доходность акций', value: 'impulseGrowVal', align: 'center', class: 'rating-val-column' },
        { text: 'Див. стабильность', value: 'dividends', align: 'center', class: 'rating-column' },
        { text: 'Див. доходность', value: 'dividendsDohodnost', align: 'center', class: 'rating-column' },
        { text: 'Долг', value: 'debt', align: 'center', class: 'rating-column' },
        { text: 'Свободный денежный поток', value: 'freeMoneyFlow', align: 'center', class: 'rating-column' },
        { text: 'Импульс роста', value: 'impulseGrow', align: 'center', class: 'rating-column' },
        { text: 'Средний рейтинг', value: 'ratingAverage', align: 'center', class: 'rating-overall' }
      ],
      snackbar: {
        enable: false,
        text: '',
        color: 'error'
      }
    }
  },
  watch: {},
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.list = await getSummaryRating()
      this.loading = false
    },
    formatCapitalization(numb) {
      return prettyNumber(numb)
    },
    getColor(figure, multiple = 1) {
      return getRatingColor(figure, multiple)
    }
  }
}
</script>

<style>

.rating-val-column {
  background-color: #d1d5ef;
}
.rating-column {
  background-color: #d2eec6;
}
.rating-main-column {
  background-color: #eee4c6;
}
.rating-overall {
  font-weight: bold;
  background-color: #eee4c6;
  color: #0d47a1;
}

</style>

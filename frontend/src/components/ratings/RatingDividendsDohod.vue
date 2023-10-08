<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col align="end" />
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
            <template v-slot:item.date="{ item }">
              {{ item.date ? new Date(item.date).toLocaleString('sv').substr(0, 10) : '' }}
            </template>
            <template v-slot:item.rating="{ item }">
              <v-chip :color="getColor(item.rating, 1)" small>{{ item.rating }}</v-chip>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { getData, endpoints } from '@/api/invmos-back'

export default {
  name: 'RatingDividendsDohod',
  data() {
    return {
      dates: [],
      years: [],
      list: [],
      headers: [],
      loading: false
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    async fetchList() {
      this.loading = true
      await this.fetchHeaders()
      this.list = await getData(endpoints.DIVIDENDS_DOHODNOST)
      this.loading = false
    },
    async fetchHeaders() {
      const curYear = new Date().getFullYear()
      this.years = [curYear - 1, curYear, curYear + 1]
      this.headers = [
        { text: 'Комапания', value: 'name' },
        { text: 'Отрасль', value: 'otrasl' },
        { text: 'Стоимость акции на текущую дату', value: 'close', align: 'center', width: 40 },
        { text: 'Дата', value: 'date', align: 'center', width: 180 },
        { text: this.years[0], value: `${this.years[0]}`, align: 'center', width: 40 },
        { text: this.years[1], value: `${this.years[1]}`, align: 'center', width: 40 },
        { text: '%', value: 'percent', align: 'center', width: 40 },
        { text: this.years[2], value: `${this.years[2]}`, align: 'center', width: 40 },
        { text: '%', value: 'percent2', align: 'center', width: 40 },
        { text: 'Рейтинг дивидендной доходности', value: 'rating', align: 'center', width: 40 },
        { text: 'Индекс мосбиржи', value: 'has_mos_index', align: 'center', width: 30 }
      ]
    },
    getColor(figure, multiple) {
      switch (figure * multiple) {
        case 0:
        case 1:
        case 2:
          return 'red lighten-3'
        case 3:
        case 4:
          return 'deep-orange lighten-3'
        case 5:
        case 6:
          return 'amber lighten-3'
        case 7:
        case 8:
          return 'lime lighten-3'
        case 9:
        case 10:
          return 'green lighten-3'
      }
    }
  }
}
</script>

<style scoped>

</style>

<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col align="end">
          <v-item-group>
            <v-btn v-if="!editMode" small dark fab color="primary" class="ms-2" @click="handleEdit"><v-icon>mdi-square-edit-outline</v-icon></v-btn>
            <v-btn v-else small dark fab color="success" class="ms-2" @click="handleSave"><v-icon>mdi-check-bold</v-icon></v-btn>
          </v-item-group>
        </v-col>
      </v-row>
      <v-row v-if="editMode">
        <v-col>
          <v-select
            v-model="coefficients"
            :items="allCoefficients"
            label="Выберите коэффициенты"
            item-value="id"
            item-text="name"
            multiple
            return-object
            chips
            hint="Коэффициенты из которых будут выбраны колонки рейтинга"
            persistent-hint
            :loading="loading"
          />
        </v-col>
        <v-col>
          <v-select
            v-model="mainCoefficientId"
            :items="coefficients"
            label="Выберите основной коэффициент"
            item-value="id"
            item-text="name"
            hint="Основной коэффициент используемый для подсчета рейтинга"
            persistent-hint
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            dense
            :disable-pagination="true"
            :items="list"
            :headers="headers"
          >
            <template v-slot:item.company.capitalization="{ item }">
              {{ formatCapitalization(item.company.capitalization) }}
            </template>
            <template v-slot:item.rating="{ item }">
              <v-chip :color="getColor(item.rating, 1)" small>{{ item.rating }}</v-chip>
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
import { getData, postData, endpoints } from '@/api/invmos-back'
import { prettyNumber } from '@/utils/prettifier'
import { getRatingCoefficientsRatings, getRatingColor } from '@/utils/ratingFiller'
export default {
  name: 'RatingByCoefficients',
  props: {
    ratingName: {
      type: String,
      default: 'debt'
    },
    useCapitalization: {
      type: Boolean,
      default: false
    },
    ratingColumnName: {
      type: String,
      default: 'Рейтинг'
    }
  },
  data() {
    return {
      list: [],
      editMode: false,
      headers: [],
      loading: false,
      coefficients: [],
      mainCoefficientId: undefined,
      allCoefficients: [],
      snackbar: {
        enable: false,
        text: '',
        color: 'error'
      }
    }
  },
  watch: {
    ratingName: function() {
      this.fetchList()
    }
  },
  created() {
    this.fetchAllData()
  },
  methods: {
    fetchAllData() {
      this.fetchCoefficients().then(
        this.fetchList()
      )
    },
    async fetchList() {
      this.loading = true
      const [columns, data] = await getRatingCoefficientsRatings(this.ratingName, this.useCapitalization)
      this.list = data

      const mainCoefficient = columns.find(c => c.is_main)
      this.mainCoefficientId = mainCoefficient ? mainCoefficient.coefficient_id : undefined

      const coefficientsIds = columns.map(c => c.coefficient_id)
      this.coefficients = this.allCoefficients.filter(c => coefficientsIds.includes(c.id))

      this.headers = [
        { text: 'Комапания', value: 'company.name' },
        { text: 'Отрасль', value: 'company.otrasl' },
        this.useCapitalization ? { text: 'Капитализация', value: 'company.capitalization' } : {},
        ...columns.map(y => ({ text: `${y.name}`, value: `data.${y.coefficient_id}.value.valueCounted` })),
        { text: this.ratingColumnName, value: 'rating', align: 'center', width: 30 }
      ]
      this.loading = false
    },
    handleEdit() {
      this.editMode = true
    },
    async handleSave() {
      if (this.coefficients.length !== 0 && this.mainCoefficientId) {
        this.editMode = false
        await postData(endpoints.RATINGS_COEFFICIENTS, {}, false, {
          name: this.ratingName,
          coefficientsIds: this.coefficients.map(c => c.id).join(','),
          mainId: this.mainCoefficientId
        })
        await this.fetchList()
      } else {
        this.snackbar.text = 'Нужно выбрать коэффициенты и основной коэффициент, используемый для подсчета рейтинга'
        this.snackbar.enable = true
      }
    },
    async fetchCoefficients() {
      this.allCoefficients = await getData(endpoints.COEFFICIENTS)
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

<style scoped>

</style>

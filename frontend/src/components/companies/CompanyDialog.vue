<template>
  <v-dialog v-if="open" v-model="temp" :eager="true" scrollable max-width="980px">
    <v-card>
      <v-card-title>
        {{ dialogModes[dialogMode] }}
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="addForm" v-model="valid" lazy-validation>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model="temp.name"
                  :rules="rules.nameRules"
                  label="Название"
                  required
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model="temp.tiker"
                  :rules="rules.tikerRules"
                  label="Тикер"
                  required
                />
              </v-col>
              <!--                  <v-col cols="12" sm="6" md="3">-->
              <!--                    <v-autocomplete-->
              <!--                      v-model="temp.currency"-->
              <!--                      no-data-text="Нет данных"-->
              <!--                      label="Выберите валюту"-->
              <!--                      :items="currencies"-->
              <!--                      clearable-->
              <!--                    />-->
              <!--                  </v-col>-->
              <!--                  <v-col cols="12" sm="6" md="3">-->
              <!--                    <v-checkbox-->
              <!--                      v-model="temp.has_mos_index"-->
              <!--                      label="Индекс МОС биржи"-->
              <!--                    />-->
              <!--                  </v-col>-->
            </v-row>
            <!--                <v-row>-->
            <!--                  <v-col cols="12" sm="6" md="6">-->
            <!--                    <v-autocomplete-->
            <!--                      v-model="temp.otrasl_id"-->
            <!--                      no-data-text="Нет данных"-->
            <!--                      label="Выберите отрасль"-->
            <!--                      :items="otrasli"-->
            <!--                      item-text="name"-->
            <!--                      item-value="id"-->
            <!--                      clearable-->
            <!--                    />-->
            <!--                  </v-col>-->
            <!--                  <v-col cols="12" sm="6" md="6">-->
            <!--                    <v-autocomplete-->
            <!--                      v-model="temp.strategies_ids"-->
            <!--                      no-data-text="Нет данных"-->
            <!--                      label="Выберите стратегии"-->
            <!--                      :items="strategies"-->
            <!--                      item-text="name"-->
            <!--                      item-value="id"-->
            <!--                      multiple-->
            <!--                      clearable-->
            <!--                    />-->
            <!--                  </v-col>-->
            <!--                </v-row>-->
            <v-card-actions>
              <v-spacer />
              <v-btn text color="warning" @click="handleDelete">Удалить</v-btn>
              <v-btn text @click="handleCancel">Отмена</v-btn>
              <v-btn text :disabled="!valid" color="primary" @click="saveItem">Сохранить</v-btn>
            </v-card-actions>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { deleteData, endpoints, postData, putData } from '@/api/invmos-back'

export default {
  name: 'CompanyDialog',
  props: {
    open: Boolean,
    editData: {
      type: Object,
      default: () => ({})
    },
    companyNames: {
      type: Array,
      default: () => ([])
    },
    companyTikers: {
      type: Array,
      default: () => ([])
    },
    dialogMode: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      valid: true,
      dialogModes: {
        add: 'Добавить компанию',
        edit: 'Редактировать компанию'
      },
      currencies: ['RUB', 'USD', 'EUR'],
      temp: {
        id: undefined,
        name: '',
        price: '',
        tiker: '',
        has_mos_index: true,
        strategies_ids: [],
        otrasl_id: undefined,
        currency: 'RUB'
      },
      rules: {
        nameRules: [
          v => !!v || 'Имя обязательно',
          v => (v && v.length >= 3) || 'Имя должно быть более 3 символов',
          v => (!this.companyNames.includes(v ? v.toLowerCase() : '')) || 'Такая компания уже есть'
        ],
        tikerRules: [
          v => !!v || 'Тикер обязателен',
          v => (v && v.length >= 3) || 'Имя должно быть более 2 символов',
          v => (!this.companyTikers.includes(v ? v.toLowerCase() : '')) || 'Компания с таким тикером уже есть'
        ]
      }
    }
  },
  computed: {},
  watch: {
    open: function() {
      this.resetTemp()
      if (this.editData) {
        this.temp = Object.assign({}, this.editData)
      }
    }
  },
  methods: {
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        price: '',
        tiker: '',
        has_mos_index: true,
        strategies_ids: [],
        otrasl_id: undefined,
        currency: 'RUB'
      }
    },
    saveItem() {
      if (this.dialogMode === 'add') this.addItem()
      else this.editItem()
    },
    addItem: function() {
      postData(endpoints.COMPANIES, this.temp)
        .then(async resp => {
          // const id = resp.id
          this.dialog = false
          // const dateFrom = new Date(Date.now() - 315569260000)
          //   .toLocaleString('sv')
          //   .substr(0, 10)
          //
          // await Promise.all([
          //   getDividends(this.temp.tiker, dateFrom, '')
          //     .then(data => postData(endpoints.DIVIDENDS_DATA, data, false, { companyId: id, type: 'data' })),
          //   this.priceSynchronizer.sync([id])
          // ])

          this.$emit('added-company')
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleCancel() {
      this.$emit('dialog-cancel')
    },
    editItem() {
      putData(endpoints.COMPANIES + this.temp.id, this.temp, false)
        .then(() => {
          this.$emit('added-company')
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete() {
      confirm('Вы точно хотите удалить?') &&
      deleteData(endpoints.COMPANIES + this.temp.id).then(() => {
        this.active = []
        this.$emit('deleted-company')
        this.dialog = false
        console.log(`Deleted`)
      })
    }
  }
}
</script>

<style scoped>

</style>

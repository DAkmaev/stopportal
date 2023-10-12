<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col>
          <v-item-group>
            <v-btn small dark fab color="primary" class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          </v-item-group>
        </v-col>
      </v-row>
      <v-data-table
        dense
        :items="list"
        :items-per-page="50"
        :headers="headers"
        item-key="name"
        :disable-pagination="true"
        :hide-default-footer="true"
        @click:row="handleEdit"
      >
        <template v-slot:item.has_mos_index="{ item }">
          <v-icon v-if="item.has_mos_index" color="primary">mdi-check</v-icon>
        </template>
      </v-data-table>
      <v-dialog v-if="dialog" v-model="dialog" :eager="true" scrollable max-width="980px">
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
    </v-container>

  </div>
</template>

<script>
import {
  getData, postData, putData, deleteData,
  // getCategoriesSimple, getStrategies,
  endpoints
} from '@/api/invmos-back'
// import { getDividends } from '@/api/open-broker'
import PriceSynchronizer from '@/utils/PriceSynchronizer'

export default {
  name: 'Companies',
  props: {},
  data() {
    return {
      priceSynchronizer: new PriceSynchronizer(),
      list: [],
      otrasli: [],
      strategies: [],
      dialog: false,
      dialogMode: '',
      dialogModes: {
        add: 'Добавить компанию',
        edit: 'Редактировать компанию'
      },
      currencies: ['RUB', 'USD', 'EUR'],
      selected: [],
      headers: [
        {
          text: 'Название',
          align: 'start',
          value: 'name'
        },
        // {
        //   text: 'Отрасль',
        //   align: 'start',
        //   value: 'otrasl'
        // },
        // {
        //   text: 'Стратегии',
        //   align: 'start',
        //   value: 'strategies_str_names'
        // },
        {
          text: 'Тикер',
          align: 'start',
          value: 'tiker'
        }
        // ,{
        //   text: 'Индекс МОС биржи',
        //   value: 'has_mos_index',
        //   align: 'center'
        // },
        // { text: 'Валюта', value: 'currency' }
      ],
      valid: true,
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
          v => (!this.companyNames.includes(v.toLowerCase())) || 'Такая компания уже есть'
        ],
        tikerRules: [
          v => !!v || 'Тикер обязателен',
          v => (v && v.length >= 3) || 'Имя должно быть более 2 символов',
          v => (!this.companyTikers.includes(v.toLowerCase())) || 'Компания с таким тикером уже есть'
        ]
      }
    }
  },
  computed: {
    otrasliKeyMap() {
      return this.otrasli.reduce(function(map, obj) {
        map[obj.id] = obj
        return map
      }, {})
    },
    companyNames() {
      return this.list.map(c => c.name.toLowerCase())
    },
    companyTikers() {
      return this.list.map(c => c.tiker.toLowerCase())
    }
  },
  created() {},
  mounted() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      // getStrategies().then(strategies => {
      //   this.strategies = strategies
      // })
      // getCategoriesSimple('otrasli').then(otrasli => {
      //   this.otrasli = otrasli
      // })
      getData(endpoints.COMPANIES).then(data => {
        this.list = data
      })
    },
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
    handleAdd() {
      this.resetTemp()
      this.dialogMode = 'add'
      this.dialog = true
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

          this.fetchList()
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(item) {
      this.dialogMode = 'edit'
      this.temp = Object.assign({}, item)
      this.dialog = true
    },
    editItem() {
      putData(endpoints.COMPANIES + this.temp.id, this.temp, false)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete() {
      confirm('Вы точно хотите удалить?') &&
        deleteData(endpoints.COMPANIES, { id: this.temp.id }).then(() => {
          this.active = []
          this.fetchList()
          this.dialog = false
          console.log(`Deleted`)
        })
    }
  }
}
</script>

<style scoped></style>

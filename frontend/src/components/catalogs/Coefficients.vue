<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col class="d-flex justify-start align-center">
          <v-btn color="primary" dark fab small class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          <!--<v-btn v-show="hasSelected" color="green" dark fab small class="ms-2" @click="handleEdit(selectedItem.id)"><v-icon>mdi-pencil</v-icon></v-btn>
          <v-btn v-show="hasSelected" color="red" dark fab small class="ms-2" @click="handleDelete(selectedItem.id)"><v-icon>mdi-delete</v-icon></v-btn>-->
        </v-col>
        <v-col>
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            class="pl-4"
            label="Поиск категории"
            flat
            clearable
            clear-icon="mdi-close-circle-outline"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            v-model="selected"
            :headers="headers"
            :items="list"
            @click:row="handleEdit"
          >
            <template v-slot:item.formulas="{ item }">
              <span>{{ item.formulas.length }}</span>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-dialog v-model="dialog" width="800px">
        <v-card>
          <v-card-title>
            {{ dialogModes[dialogMode] }}
          </v-card-title>
          <v-container>
            <v-form ref="addForm" v-model="valid" lazy-validation>
              <v-row>
                <v-col cols="24" sm="12" md="12">
                  <v-text-field
                    v-model="temp.name"
                    :rules="rules.nameRules"
                    label="Название"
                    required
                  />
                </v-col>
              </v-row>
              <!--<v-divider></v-divider>-->
              <div v-for="(formula, i) in temp.formulas" :key="i">
                <v-row :key="i" class="d-flex justify-center align-center">
                  <v-col cols="12" sm="8" md="8">
                    <v-textarea
                      v-model="formula.value"
                      auto-grow
                      rows="1"
                      dense
                      outlined
                      single-line
                      append-outer-icon="mdi-trash-can-outline"
                      hide-details="auto"
                      @click:append-outer="removeFormula(formula, i)"
                    />
                  </v-col>
                </v-row>
              </div>
              <v-row class="d-flex justify-center align-center">
                <v-col cols="12" sm="8" md="8">
                  <v-btn text small color="primary" @click="addFormula">Добавить формулу</v-btn>
                </v-col>
              </v-row>
              <v-card-actions>
                <v-spacer />
                <v-btn text color="warning" @click="handleDelete(temp.id)">Удалить</v-btn>
                <v-btn text color="primary" @click="handleCancel">Отмена</v-btn>
                <v-btn
                  text
                  :disabled="!valid"
                  @click="saveItem"
                >Сохранить</v-btn>
              </v-card-actions>
            </v-form>
          </v-container>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { getData, postData, putData, deleteData, endpoints } from '@/api/invmos-back'
export default {
  name: 'Coefficients',
  data() {
    return {
      dialog: false,
      valid: true,
      dialogMode: '',
      dialogModes: {
        add: 'Добавить коэффициэнт',
        edit: 'Редактировать коэффициэнт'
      },
      fab: false,
      search: null,
      selected: [],
      list: [],
      temp: {
        id: null,
        name: '',
        description: null,
        formulas: []
      },
      rules: {
        nameRules: [
          v => !!v || 'Имя обязательно',
          v => (v && v.length >= 3) || 'Имя должно быть более 3 символов'
        ]
      },
      headers: [
        {
          text: 'Id',
          align: 'center',
          width: 30,
          value: 'id'
        },
        { text: 'Название', value: 'name' },
        { text: 'Количество формул', value: 'formulas' }
      ]
    }
  },
  computed: {
    filter() {
      return this.caseSensitive
        ? (item, search, textKey) => item[textKey].indexOf(search) > -1
        : undefined
    },
    selectedItem() {
      return this.selected && this.selected.length > 0 ? this.selected[0] : null
    },
    hasSelected() {
      return this.selectedItem !== null
    }
  },
  watch: {
    type: function() {
      this.fetchList()
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      getData(endpoints.COEFFICIENTS, { type: this.type }).then(data => {
        this.list = data
      })
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
      postData(endpoints.COEFFICIENTS, this.temp, false)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    resetTemp() {
      this.temp = {
        id: null,
        name: '',
        description: null,
        formulas: []
      }
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(item) {
      this.temp = this.list.find(l => l.id === item.id)
      this.dialogMode = 'edit'
      this.dialog = true
    },
    editItem() {
      putData(endpoints.COEFFICIENTS, this.temp, false)
        .then(() => {
          this.fetchList()
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete(id) {
      confirm('Вы точно хотите удалить?') &&
      deleteData(endpoints.COEFFICIENTS, { id: id }).then(() => {
        this.active = []
        this.dialog = false
        this.fetchList()
        console.log(`Deleted ${this.list.find(item => item.id === id).name}`)
      })
    },
    addFormula() {
      this.temp.formulas.push({ id: undefined, value: '' })
    },
    removeFormula(formula, index) {
      confirm('Вы точно хотите удалить?') && this.temp.formulas.splice(index, 1)
    }
  }
}
</script>

<style scoped>

</style>

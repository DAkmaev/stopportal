<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col class="d-flex justify-start align-center">
          <v-btn color="primary" dark fab small class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          <v-btn v-show="hasSelected" color="green" dark fab small class="ms-2" @click="handleEdit(selectedItem.id)"><v-icon>mdi-pencil</v-icon></v-btn>
          <v-btn v-show="hasSelected" color="red" dark fab small class="ms-2" @click="handleDelete(selectedItem.id)"><v-icon>mdi-delete</v-icon></v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-data-table
            v-model="selected"
            :headers="headers"
            :items="list"
            show-select
            single-select
            :disable-pagination="false"
            :hide-default-footer="true"
          />
        </v-col>
      </v-row>
      <v-dialog v-model="dialog" width="800px">
        <v-card>
          <v-card-title>
            {{ dialogModes[dialogMode] }}
          </v-card-title>
          <v-container>
            <v-form ref="addForm" v-model="valid" lazy-validation>
              <v-text-field
                v-model="temp.name"
                :rules="rules.nameRules"
                label="Название"
                required
              />
              <v-card-actions>
                <v-spacer />
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
import { postData, putData, deleteData, endpoints, getData } from '@/api/invmos-back'
import { mapGetters } from 'vuex'
export default {
  name: 'Strategies',
  props: {
    type: {
      type: String,
      default: undefined
    }
  },
  data() {
    return {
      dialog: false,
      valid: true,
      dialogMode: '',
      dialogModes: {
        add: 'Добавить стратегию',
        edit: 'Редактировать стратегию'
      },
      fab: false,
      search: null,
      selected: [],
      list: [],
      temp: {
        id: null,
        name: '',
        description: null
      },
      rules: {
        nameRules: [
          v => !!v || 'Имя обязательно',
          v => (v && v.length >= 3) || 'Имя должно быть более 3 символов'
        ]
      },
      headers: [{ text: 'Название', value: 'name' }]
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
    ...mapGetters(['token']),
    fetchList() {
      getData(endpoints.STRATEGIES, null, this.token).then(data => {
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
      postData(endpoints.STRATEGIES, this.temp, { type: this.type }, this.token)
        .then(() => {
          this.$nextTick(() => {
            this.fetchList()
          })
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
        description: null
      }
    },
    handleCancel() {
      this.dialog = false
    },
    handleEdit(id) {
      this.temp = this.list.find(l => l.id === id)
      this.dialogMode = 'edit'
      this.dialog = true
    },
    editItem() {
      putData(endpoints.STRATEGIES + this.temp.id, this.temp, this.token)
        .then(() => {
          this.$nextTick(() => {
            this.fetchList()
          })
          this.dialog = false
        })
        .catch(err => {
          console.error(err)
        })
    },
    handleDelete(id) {
      confirm('Вы точно хотите удалить?') &&
      deleteData(endpoints.STRATEGIES + id, this.token)
        .then(() => {
          this.active = []
          this.selected = []
          this.$nextTick(() => {
            this.fetchList()
          })
          console.log(`Deleted ${this.list.find(item => item.id === id).name}`)
        })
    }
  }
}
</script>

<style scoped>

</style>

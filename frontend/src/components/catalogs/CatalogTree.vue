<template>
  <div>
    <v-container fluid>
      <v-row>
        <v-col class="d-flex justify-start align-center">
          <v-btn color="primary" dark fab small class="ms-2" @click="handleAdd"><v-icon>mdi-plus</v-icon></v-btn>
          <v-btn v-show="hasActivated" color="green" dark fab small class="ms-2" @click="handleEdit(activated)"><v-icon>mdi-pencil</v-icon></v-btn>
          <v-btn v-show="hasActivated" color="red" dark fab small class="ms-2" @click="handleDelete(activated)"><v-icon>mdi-delete</v-icon></v-btn>
        </v-col>
        <v-col>
          <v-text-field
            v-model="search"
            prepend-inner-icon="mdi-magnify"
            class="pl-4"
            label="Поиск статьи"
            flat
            clearable
            clear-icon="mdi-close-circle-outline"
          />
        </v-col>
      </v-row>
      <v-treeview
        :active.sync="active"
        :items="tree"
        hoverable
        activatable
        shaped
        dense
        :search="search"
        :filter="filter"
        :open.sync="open"
        expand-icon="mdi-chevron-down"
        on-icon="mdi-bookmark"
        off-icon="mdi-bookmark-outline"
        indeterminate-icon="mdi-bookmark-minus"
      >
        <template v-slot:prepend="{ item, isOpen }">
          <v-icon v-if="item.children && item.children.length > 0">
            {{ isOpen ? 'mdi-folder-open' : 'mdi-folder' }}
          </v-icon>
        </template>
        <template v-slot:label="{ item }">
          <span>{{ item.name }} ({{ item.id }})</span>
        </template>
      </v-treeview>
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
              <v-autocomplete
                v-model="temp.parent_id"
                no-data-text="Нет данных"
                label="Выберите группу"
                :items="list"
                item-text="name"
                item-value="id"
                clearable
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
import { getData, postData, putData, deleteData, endpoints } from '@/api/invmos-back'
import { nest } from '@/utils/tree'
export default {
  name: 'CatalogTree',
  props: {
    type: {
      type: String,
      default: undefined
    }
  },
  data() {
    return {
      // type: "balance",
      dialog: false,
      valid: true,
      dialogMode: '',
      dialogModes: {
        add: 'Добавить категорию',
        edit: 'Редактировать категорию'
      },
      fab: false,
      active: [],
      open: [],
      search: null,
      list: [],
      tree: [],
      temp: {
        id: null,
        name: '',
        parent_id: null
      },
      rules: {
        nameRules: [
          v => !!v || 'Имя обязательно',
          v => (v && v.length >= 3) || 'Имя должно быть более 3 символов'
        ]
      }
    }
  },
  computed: {
    filter() {
      return this.caseSensitive
        ? (item, search, textKey) => item[textKey].indexOf(search) > -1
        : undefined
    },
    activated() {
      return this.active && this.active.length > 0 ? this.active[0] : null
    },
    hasActivated() {
      return this.activated !== null
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
      getData(endpoints.CATEGORIES, { type: this.type })
        .then(data => {
          this.list = data
          this.tree = nest(data)
        })
    },
    handleAdd() {
      this.resetTemp()
      this.temp.parent_id = this.active.length > 0 ? this.list.find(e => e.id === this.active[0]).id : null
      this.dialogMode = 'add'
      this.dialog = true
    },
    saveItem() {
      if (this.dialogMode === 'add') this.addItem()
      else this.editItem()
    },
    addItem() {
      postData(endpoints.CATEGORIES, this.temp, false, { type: this.type })
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
        parent_id: null
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
      putData(endpoints.CATEGORIES, this.temp, false)
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
      deleteData(endpoints.CATEGORIES, { id: id })
        .then(() => {
          this.active = []
          this.fetchList()
          console.log(`Deleted ${this.list.find(item => item.id === id).name}`)
        })
    }
  }
}
</script>

<style scoped></style>

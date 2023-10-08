<template>
  <div>
    <v-row class="pa-4" justify="space-between">
      <v-col>
        <v-row v-show="!noTreeChanges">
          <v-btn small class="ml-3 mb-3" color="success" @click="handleSaveTree">Сохранить</v-btn>
          <v-btn small class="ml-3 mb-3" color="normal" @click="handleResetTree">Отменить</v-btn>
        </v-row>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-scroll-y-transition mode="out-in">
          <v-treeview
            v-model="selection"
            dense
            :items="tree"
            selectable
            open-all
            @input="changedSelection = true"
          />
        </v-scroll-y-transition>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { getData, putData, endpoints } from '@/api/invmos-back'
import { nest } from '@/utils/tree'
export default {
  name: 'CompanyCategories',
  props: {
    reportType: {
      type: String,
      default: undefined
    },
    companyId: {
      type: Number,
      default: undefined
    }
  },
  data() {
    return {
      list: [],
      selectionType: 'leaf', // 'independent'
      selection: [],
      selection_original: [],
      tree: [],
      changedSelection: false
    }
  },
  computed: {
    noTreeChanges() {
      const selection = this.selection_original.length === this.selection.length ? this.selection_original : null
      const _this = this
      return selection && selection.every(function(value, index) { return value === _this.selection.sort()[index] })
    }
  },
  created() {
  },
  mounted() {
    Promise.all([this.fetchCategories(), this.fetchCategoriesValues()])
  },
  methods: {
    async fetchCategories() {
      getData(endpoints.CATEGORIES, { type: this.reportType }).then(data => {
        this.tree = nest(data)
      })
    },
    fetchCategoriesValues() {
      this.selection = []
      this.selection_original = []
      this.changedSelection = false
      if (this.companyId !== undefined) {
        getData(endpoints.COMPANIES_CATEGORIES, { type: this.reportType, companyId: this.companyId }).then(data => {
          this.selection_original = data.map(v => v.category_id)
          this.selection = this.selection_original
        })
      }
    },
    handleSaveTree() {
      putData(endpoints.COMPANIES_CATEGORIES, {}, {
        reportType: this.reportType,
        companyId: this.companyId,
        selection: this.selection,
        selection_original: this.selection_original
      }).then(() => {
        this.selection_original = this.selection
        this.$emit('save-categories')
      })
    },
    handleResetTree() {
      this.selection = this.selection_original
      this.$emit('cancel-save')
    }
  }
}
</script>

<style scoped>

</style>

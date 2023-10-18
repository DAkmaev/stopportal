<template>
  <v-dialog v-model="stops" scrollable max-width="980px">
    <v-card>
      <v-card-title>
        Изменить стопы для {{ tiker }}
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
            </v-row>
            <v-card-actions>
              <v-spacer />
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
export default {
  name: "CompanyStops",
  props: {
    tiker: {
      type: String
    },
    stops: {
      type: Array,
      default: []
    }
  },
}
</script>

<style scoped>

</style>
import { getData, endpoints } from '@/api/invmos-back'
import MParser from '@/utils/parser/MParser'
const mparser = new MParser()

export const fillReportCoefficientFormulas = async(list, companyId, multiplier = 1) => {
  let needRepeatAll = true
  let hasChanges = true
  while (needRepeatAll && hasChanges) {
    hasChanges = false
    needRepeatAll = false
    for (const l of list) {
      for (const [k, v] of Object.entries(l.values)) {
        const [changed, requireCoefficient] = await fillValueCounted(v, k, companyId, multiplier, list)
        hasChanges = hasChanges || changed
        needRepeatAll = needRepeatAll || !!requireCoefficient
      }
    }
  }
  return list
}

export const fillRatingFormulas = async(list, multiplier = 1) => {
  for (const l of list) {
    let needRepeatAll = true
    let hasChanges = true
    while (needRepeatAll && hasChanges) {
      hasChanges = false
      const coefficientList = Object.values(l.data)
      for (const [k, d] of Object.entries(l.data)) {
        if (d) {
          console.log(k)
          const [changed, requireCoefficient] = await fillValueCounted(d.value, d.date, l.company.id, multiplier, coefficientList)
          hasChanges = hasChanges || changed
          needRepeatAll = needRepeatAll || !!requireCoefficient
          if (requireCoefficient) { coefficientList.push(requireCoefficient) }
        }
      }
    }
  }
  return list
}

export const fillValueCounted = async(valueBlock, date, companyId, multiplier, list) => {
  let hasChanges = false
  let requireCoefficient = null
  if (typeof valueBlock.valueCounted === 'undefined') {
    const formula = valueBlock && valueBlock.value ? valueBlock.value : (valueBlock && valueBlock.formula ? valueBlock.formula.value : null)
    if (formula) {
      const regexp = /[а-яА-ЯёЁ]+\d+/ig
      let result
      let filledAllVariables = true
      while ((result = regexp.exec(formula))) {
        const varValue = await fillVariables(result[0], date, list, companyId)
        if (varValue) { mparser.setVariable(result[0], varValue.value) } else
        if (varValue.requiredCoefficient) {
          requireCoefficient = varValue.requiredCoefficient
          filledAllVariables = false
        } else { filledAllVariables = false }
      }
      if (filledAllVariables) {
        const result = mparser.Parse(formula)
        valueBlock.valueCounted = result ? multiplyValue(result, multiplier) : result
        hasChanges = true
      }
    } else {
      valueBlock.valueCounted = ''
      hasChanges = true
    }
  }
  return [hasChanges, requireCoefficient]
}

export const fillVariables = async(variable, date, list, companyId) => {
  const result = { value: null, requiredCoefficient: null }
  const catalogPref = /[а-яА-Я]+/gi.exec(variable)[0]
  const idPref = Number.parseInt(/\d+/gi.exec(variable)[0])
  const returnReportValue = async(catalog) => {
    const value = await getData(endpoints.REPORTS_VALUE, {
      type: catalog,
      companyId: companyId,
      categoryId: idPref,
      date: date
    })
    return value.length > 0 ? value[0].value : ''
  }
  const returnCoefficientValue = async(companyId, date, coefficientId) => {
    const value = await getData(endpoints.COEFFICIENTS_VALUES, {
      companyId: companyId,
      date: date,
      coefficientId: coefficientId
    })
    return value.length > 0 ? value[0] : ''
  }
  switch (catalogPref) {
    case 'б': {
      result.value = returnReportValue('balance')
      break
    }
    case 'д': {
      result.value = returnReportValue('ddu')
      break
    }
    case 'п': {
      result.value = returnReportValue('piu')
      break
    }
    case 'к': {
      let coefficientData = list.find(l => l.coefficient.id === idPref)
      if (!coefficientData) {
        coefficientData = await returnCoefficientValue(companyId, date, idPref)
        result.requiredCoefficient = coefficientData
      } else {
        const value = coefficientData ? (coefficientData.value ? coefficientData.value : (coefficientData.values[date] ? coefficientData.values[date] : null)) : null
        result.value = value && value.valueCounted ? value.valueCounted : null
      }
      break
    }
  }
  return result
}

export const multiplyValue = (value, multiplier) => {
  if (multiplier === 1) { return value }

  const valNumber = typeof value === 'string' ? Number.parseFloat(value) : value
  return valNumber ? (valNumber / multiplier).toString() : value
}

import { getData, endpoints } from '@/api/invmos-back'
import { fillRatingFormulas } from '@/utils/coefficientFiller'

export const getRatingCoefficientsRatings = async(ratingName, useCapitalization) => {
  const result = await getData(endpoints.RATINGS_COEFFICIENTS, { name: ratingName, useCapitalization: useCapitalization })
  const data = await fillRatingFormulas(result.data)
  const mainColId = result.columns.length > 0 ? result.columns.find(c => c.is_main).coefficient_id : null

  data.sort((a, b) => a.data[mainColId].value.valueCounted > b.data[mainColId].value.valueCounted ? -1 : 0)

  let previous = null
  const step = data.length / 10
  data.forEach((l, idx, arr) => {
    const val = l.data[mainColId].value.valueCounted
    if (previous === val && previous !== null) {
      Object.assign(l, { rating: arr[idx - 1].rating, ratingValue: val })
    } else {
      const fig = Number.parseInt((data.length - idx) / step)
      Object.assign(l, { rating: fig === 10 ? fig : fig, ratingValue: val })
    }
    previous = val
  })

  return [result.columns, data]
}

export const getRatingColor = (figure, multiple) => {
  const val = figure * multiple
  switch (true) {
    case (val >= 0 && val < 3):
      return 'lighten-3 red'
    case (val >= 3 && val < 5):
      return 'lighten-3 deep-orange'
    case (val >= 5 && val < 7):
      return 'lighten-3 amber'
    case (val >= 7 && val < 9):
      return 'lighten-3 lime'
    case (val >= 9):
      return 'lighten-3 green'
  }
}

export const getSummaryRating = async() => {
  const [companies, freeMoneyFlow, debt, impulseGrow, dividendsDohodnost, dividends] = await Promise.all([
    getData(endpoints.COMPANIES, { fields: 'c.id,c.name,o.id as otrasl_id,o.name as otrasl' }),
    getRatingCoefficientsRatings('freeMoneyFlow', true),
    getRatingCoefficientsRatings('debt', false),
    getData(endpoints.RATINGS_IMPULSE_GROW),
    getData(endpoints.DIVIDENDS_DOHODNOST),
    getData(endpoints.DIVIDENDS_OVERALL)
  ])

  const summList = companies.reduce((res, c) => {
    res[c.name] = {
      company_id: c.id,
      name: c.name,
      otrasl: c.otrasl,
      freeMoneyFlow: 0,
      freeMoneyFlowVal: 0,
      debt: 0,
      debtVal: 0,
      impulseGrow: 0,
      impulseGrowVal: 0,
      dividendsDohodnost: 0,
      dividendsDohodnostVal: 0,
      dividends: 0,
      dividendsVal: 0,
      ratingAverage: 0
    }
    return res
  }, {})

  freeMoneyFlow[1].forEach(item => {
    summList[item.company.name].freeMoneyFlow = item.rating
    summList[item.company.name].freeMoneyFlowVal = item.ratingValue
  })
  debt[1].forEach(item => {
    summList[item.company.name].debt = item.rating
    summList[item.company.name].debtVal = item.ratingValue
  })
  impulseGrow.forEach(item => {
    summList[item.name].impulseGrow = item.rating
    summList[item.name].impulseGrowVal = item.ratingValue
  })
  dividendsDohodnost.forEach(item => {
    summList[item.name].dividendsDohodnost = item.rating
    summList[item.name].dividendsDohodnostVal = item.ratingValue
  })
  dividends[1].forEach(item => {
    summList[item.name].dividends = item.rating
    summList[item.name].dividendsVal = item.ratingValue
  })

  for (const [key, s] of Object.entries(summList)) {
    console.log(key)
    s['ratingAverage'] = Math.round((s.freeMoneyFlow + s.debt + s.impulseGrow + s.dividendsDohodnost + s.dividends) / 5 * 100, 2) / 100
  }

  return Object.values(summList).sort((a, b) => a.ratingAverage > b.ratingAverage ? -1 : 0)
}

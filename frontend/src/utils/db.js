const knex = require('knex')({
  client: 'mysql',
  connection: {
    host: '127.0.0.1',
    user: 'root',
    password: '',
    database: 'invmos'
  },
  debug: true
})

// COMPANIES
export const queryAllCompanies = (
  ids = null,
  tikers = null,
  fields = ['c.id', 'c.name', 'c.price', 'c.has_mos_index', 'c.tiker', 'c.currency', 'o.id as otrasl_id', 'o.name as otrasl', 'c.issue_size', 'c.capitalization']
) => {
  return new Promise((resolve, reject) => {
    const builder = knex
      .column(...fields)
      .column(knex.raw('GROUP_CONCAT(cs.strategy_id) as strategies_str_ids'))
      .column(knex.raw("GROUP_CONCAT(cat.name SEPARATOR ', ') as strategies_str_names"))
      .select()
      .from('companies as c')
      .leftJoin('companies_strategies as cs', 'cs.company_id', 'c.id')
      .leftJoin('strategies as cat', 'cat.id', 'cs.strategy_id')
      .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')
      .groupBy('c.name')
      .orderBy('c.name')

    if (ids) { builder.whereIn('c.id', ids) }

    if (tikers) { builder.whereIn('c.tiker', tikers) }

    builder
      .then(rows => {
        for (const row of rows) {
          row.strategies_ids = row.strategies_str_ids ? row.strategies_str_ids.split(',').map(s => Number.parseInt(s)) : []
        }
        resolve(rows || [])
      })
      .catch(error => {
        reject(error)
      })
  })
}

export const insertCompany = company => {
  return new Promise((resolve, reject) => {
    knex
      .insert({
        name: company.name,
        has_mos_index: company.has_mos_index ? true : null,
        tiker: company.tiker,
        otrasl_id: company.otrasl_id ? company.otrasl_id : null,
        currency: company.currency
      })
      .into('companies')
      .then(async() => {
        const insertData = await knex.raw('SELECT LAST_INSERT_ID() as ID').then(console.log('get last insert id'))
        const companyId = insertData[0][0].ID
        if (company.strategies_ids.length > 0) {
          await knex('companies_strategies')
            .insert(company.strategies_ids.map(cid => ({ company_id: companyId, strategy_id: cid })))
            .then(console.log('Company strategii added'))
        }
        resolve(companyId)
      })
  })
}

export const updateCompany = async company => {
  await knex('companies')
    .update({
      name: company.name,
      has_mos_index: company.has_mos_index ? true : null,
      tiker: company.tiker,
      otrasl_id: company.otrasl_id ? company.otrasl_id : null,
      currency: company.currency
    })
    .where('id', company.id)
    .then(
      updateCompanyStrategies(company)
    )
}

export const deleteCompany = async id => {
  return knex('companies_strategies')
    .del()
    .where('company_id', id)
    .then(() => {
      knex('companies')
        .where('id', id)
        .del()
        .then(console.log('Company deleted'))
    })
}

export const updateCompanyStrategies = async company => {
  await knex('companies_strategies')
    .del()
    .where('company_id', company.id)
    .then(() => {
      if (company.strategies_ids.length > 0) {
        knex('companies_strategies')
          .insert(company.strategies_ids.map(cid => ({ company_id: company.id, strategy_id: cid })))
          .then(console.log('Company strategies updated'))
      }
    })
}

// LAST SYNC DATE
export const getLastSyncDateIso = (id, fromDefault = 31556926000) => {
  return new Promise((resolve, reject) => {
    knex
      .select('last_date')
      .from('last_sync')
      .where({ id: id })
      .then(row => {
        const lastDateVal =
          row.length > 0
            ? new Date(row[0].last_date).toLocaleString('sv').substr(0, 10)
            : new Date(Date.now() - fromDefault).toLocaleString('sv').substr(0, 10) // one year
        resolve(lastDateVal)
      })
      .catch(error => {
        reject(error)
      })
  })
}

// PRICES
export async function insertPrices(prices, issueSize, lotSize, capitalization, companyId, updateLastDate = true) {
  const lastSyncId = 1
  await knex.transaction(async trx => {
    const rows = []
    prices.forEach(p => {
      rows.push({
        date: p.date,
        company_id: p.company_id,
        close: p.close,
        open: p.open,
        low: p.low,
        high: p.high
      })
    })
    await knex
      .raw(
        knex('prices')
          .insert(rows)
          .toString()
          .replace('insert', 'INSERT IGNORE')
      )
      .transacting(trx)

    await knex('companies')
      .update({ 'issue_size': issueSize, 'lot_size': lotSize, 'capitalization': capitalization })
      .where('id', companyId)
      .transacting(trx)

    if (updateLastDate) {
      await knex('last_sync')
        .update('last_date', new Date(Date.now()).toLocaleString('sv').substr(0, 10))
        .where('id', lastSyncId)
        .transacting(trx)
    }
  })
}

export const queryAllPrices = (
  dateFrom = undefined,
  dateTo = undefined,
  company = undefined,
  fields = ['p.id', 'p.date', 'p.company_id', 'p.close', 'p.open', 'p.low', 'p.high', 'c.currency']
) => {
  return new Promise((resolve, reject) => {
    const builder = knex
      .select(...fields)
      .from('prices as p')
      .innerJoin('companies as c', 'c.id', 'p.company_id')
      .orderBy('date', 'desc') // .where('1')

    if (dateFrom !== undefined && dateFrom !== '') { builder.andWhere('date', '>=', dateFrom) }

    if (dateTo !== undefined && dateTo !== '') { builder.andWhere('date', '<=', dateTo) }

    if (company !== undefined && company !== '') { builder.andWhere('company_id', '=', company) }

    builder
      .then(rows => {
        resolve(rows || [])
      })
      .catch(error => {
        reject(error)
      })
  })
}

export async function insertPricesDataMoex(pricesData, issueSize, lotSize, companyId, updateLastDate) {
  const prices = pricesData.map(p => {
    return {
      date: new Date(p.TRADEDATE),
      company_id: companyId,
      close: p.CLOSE,
      open: p.OPEN,
      low: p.LOW,
      high: p.HIGH
    }
  })
  return await insertPrices(prices, issueSize, lotSize, null, companyId, updateLastDate)
}
export async function insertPricesDataNyse(pricesData, capitalization, companyId, updateLastDate) {
  const prices = pricesData.map(p => {
    return {
      date: new Date(p.datetime),
      company_id: companyId,
      close: p.close,
      open: p.open,
      low: p.low,
      high: p.high
    }
  })
  return await insertPrices(prices, null, 1, capitalization, companyId, updateLastDate)
}

// DIVIDENDS
export const queryAllDividends = (
  dateFrom = undefined,
  dateTo = undefined,
  company = undefined,
  fields = [
    'id',
    'date_fixing',
    'date_can_buy',
    'company_id',
    'payment',
    'period_months',
    'period_year',
    'last_price',
    'profit'
  ]
) => {
  return new Promise((resolve, reject) => {
    const builder = knex
      .select(...fields)
      .from('dividends')
      .orderBy('date_fixing', 'desc')

    if (dateFrom !== undefined && dateFrom !== '') { builder.andWhere('date_fixing', '>=', dateFrom) }

    if (dateTo !== undefined && dateTo !== '') { builder.andWhere('date_fixing', '<=', dateTo) }

    if (company !== undefined && company !== '') { builder.andWhere('company_id', '=', company) }

    builder
      .then(rows => {
        resolve(rows || [])
      })
      .catch(error => {
        reject(error)
      })
  })
}

export async function insertDividends(dividends) {
  const lastSyncId = 2
  await knex.transaction(async trx => {
    const rows = []
    dividends.forEach(d => {
      rows.push({
        company_id: d.company_id,
        date_fixing: d.date_fixing,
        date_can_buy: d.date_can_buy,
        payment: d.payment ? d.payment : null,
        period_months: d.period_months ? d.period_months : null,
        period_year: d.period_year,
        last_price: d.last_price ? d.last_price : null,
        profit: d.profit ? null : d.profit
      })
    })

    await knex
      .raw(
        knex('dividends')
          .insert(rows)
          .toString()
          .replace('insert', 'INSERT IGNORE')
      )
      .transacting(trx)

    await knex('last_sync')
      .update('last_date', new Date(Date.now()).toLocaleString('sv').substr(0, 10))
      .where('id', lastSyncId)
      .transacting(trx)
  })
}
export async function updateDividends(dividend) {
  await knex('dividends')
    .update({
      company_id: dividend.company_id,
      date_fixing: dividend.date_fixing,
      date_can_buy: dividend.date_can_buy,
      payment: dividend.payment ? dividend.payment : null,
      period_months: dividend.period_months ? dividend.period_months : null,
      period_year: dividend.period_year,
      last_price: dividend.last_price ? dividend.last_price : null,
      profit: dividend.profit ? dividend.profit : null
    })
    .where({ id: dividend.id })
}
export async function deleteDividends(id) {
  await knex('dividends')
    .where('id', id)
    .del()
    .then(console.log('Dividends deleted'))
}
export async function insertDividendsData(dividendsData, companyId) {
  const dividends = dividendsData.map(h => {
    const dividend = {
      date_fixing: h.FixingDate,
      date_can_buy: h.LastDayCanBuy,
      company_id: companyId,
      payment: h.PaymentPerUnit,
      last_price: h.LastPrice,
      profit: h.PaymentProfitability
    }
    const period = h.PaymentPeriod ? h.PaymentPeriod.match(/(\d{1,2})\sмесяц.*(\d{4})/y) : null
    if (period) {
      dividend['period_months'] = period[1]
      dividend['period_year'] = period[2]
    }
    return dividend
  })
  return insertDividends(dividends)
}

// CATEGORIES
export const getCategories = async type => {
  return knex
    .withRecursive('ancestors', qb => {
      qb.select('*')
        .from('categories')
        .where('categories.parent_id', null)
        .andWhere('type', type)
        .unionAll(qb => {
          qb.select('categories.*')
            .from('categories')
            .join('ancestors', 'ancestors.id', 'categories.parent_id')
        })
    })
    .select('*')
    .from('ancestors')
    .then(console.log('Get categories'))
    .catch(error => {
      console.log(`Get categories error: ${error}`)
    })
}
export async function insertCategory(category, type) {
  await knex('categories')
    .insert({
      name: category.name,
      type: type,
      parent_id: category.parent_id ? category.parent_id : null
    })
    .then(console.log('Category saved'))
}
export async function updateCategory(category) {
  await knex('categories')
    .update({
      name: category.name,
      parent_id: category.parent_id
    })
    .where({ id: category.id })
    .then(console.log('Category saved'))
}
export async function deleteCategory(id) {
  await knex('categories')
    .where('id', id)
    .del()
    .then(console.log('Category deleted'))
}

// CATEGORIES SIMPLE
export const getCategoriesSimple = async type => {
  return knex('categories_simple')
    .where('type', type)
    .orderBy('name')
    .then(console.log(`Get categories for ${type}`))
}
export async function insertCategorySimple(category, type) {
  await knex('categories_simple')
    .insert({
      name: category.name,
      type: type,
      description: category.description ? category.description : null
    })
    .then(console.log(`Category ${category.name} saved`))
}
export async function updateCategorySimple(category) {
  await knex('categories_simple')
    .update({
      name: category.name,
      description: category.description ? category.description : null
    })
    .where({ id: category.id })
    .then(console.log(`Category ${category.name} saved`))
}
export async function deleteCategorySimple(id) {
  await knex('categories_simple')
    .where('id', id)
    .del()
    .then(console.log('Category deleted'))
}

// REPORTS
export const getReportColumns = async(type, companyId) => {
  return knex('reports_columns')
    .where('type', type)
    .andWhere('company_id', companyId)
    .orderBy('date', 'asc')
    .then(console.log('Get report columns'))
}
export async function getReportValues(type, companyId, columns) {
  const colArray = columns.map(c => {
    const col = {}
    col[`d_${c.id}`] = `d_${c.id}.value`
    return col
  })

  const builder = knex.columns('c.id', 'cc.id as company_category_id', 'c.parent_id', 'c.name', ...colArray)
    .distinct('c.id')
    .from(function() {
      this.withRecursive('ancestors', qb => {
        qb.select('*')
          .from('categories')
          .whereIn('categories.id', function() {
            this.select('category_id').from('companies_categories').where('type', type).andWhere('company_id', companyId)
          })
          .unionAll(qb => {
            qb.select('categories.*')
              .from('categories')
              .join('ancestors', 'ancestors.parent_id', 'categories.id')
          })
      }).from('ancestors').as('c')
    })
    .leftJoin('companies_categories as cc', 'cc.category_id', 'c.id')
    .where('cc.company_id', companyId).orWhereNull('cc.company_id')

  columns.forEach(c => {
    const asName = `d_${c.id}`
    builder.leftJoin(function() {
      this.from('reports_values').where('report_column_id', c.id).as(asName)
    }, `${asName}.companies_category_id`, 'cc.id')
  })

  return builder
}
export async function getReportValue(type, companyId, categoryId, date) {
  return knex.column('cc.company_id', 'rc.date', 'rv.value')
    .from('reports_values as rv')
    .innerJoin('reports_columns as rc', 'rc.id', 'rv.report_column_id')
    .innerJoin('companies_categories as cc', 'cc.id', 'rv.companies_category_id')
    .innerJoin('categories as c', 'c.id', 'cc.category_id')
    .where('rc.company_id', companyId)
    .andWhere('rc.date', new Date(date).toLocaleString('sv').substr(0, 10))
    .andWhere('c.id', categoryId)
    .then(console.log(''))
}
export async function updateReportValue(categoryId, columnId, value) {
  if (value === '') {
    knex('reports_values')
      .where('companies_category_id', categoryId)
      .andWhere('report_column_id')
      .del().then(console.log('Report value was deleted'))
  } else {
    knex('reports_values')
      .count('id as count')
      .where('companies_category_id', categoryId)
      .andWhere('report_column_id', columnId)
      .then(data => {
        if (data[0].count > 0) {
          knex('reports_values')
            .update('value', value)
            .where('companies_category_id', categoryId)
            .andWhere('report_column_id', columnId)
            .then('Updated reports_values value')
        } else {
          knex('reports_values')
            .insert({ companies_category_id: categoryId, report_column_id: columnId, value: value })
            .then('Inserted reports_values value')
        }
      })
  }
}
export async function insertReportColumn(type, companyId, date) {
  knex('reports_columns')
    .insert({
      'type': type, 'company_id': companyId, 'date': date
    }).then()
}

export const getReportUnit = async(type, companyId) => {
  return knex('reports_units')
    .column('unit')
    .where('company_id', companyId)
    .andWhere('type', type)
    .then(console.log('Get report unit'))
}
export const setReportUnit = async(type, companyId, unit) => {
  return knex('reports_units')
    .del()
    .where('company_id', companyId)
    .andWhere('type', type)
    .then(() => {
      return knex('reports_units')
        .insert({ 'type': type, 'company_id': companyId, 'unit': unit })
    }).then(console.log('Set report unit'))
}

// COMPANY CATEGORIES
export const getCompanyCategories = async(type, companyId) => {
  return knex('companies_categories')
    .where('type', type)
    .andWhere('company_id', companyId)
    .then(console.log('Get companies_categories'))
}
export const updateCompanyCategories = async(type, companyId, newValues, oldValues = undefined) => {
  if (oldValues === undefined || oldValues === null) { oldValues = await getCompanyCategories(type, companyId).map(v => v.category_id) }

  const toDelete = oldValues.filter(c => !newValues.includes(c))
  const toInsert = newValues.filter(c => !oldValues.includes(c)).map(c => {
    return { category_id: c, company_id: companyId, type: type }
  })
  return Promise.all([
    knex('companies_categories')
      .insert(toInsert)
      .then(console.log(`Inserted companies_categories: ${toInsert}`)),
    knex('companies_categories')
      .whereIn('category_id', toDelete)
      .andWhere('company_id', companyId)
      .andWhere('type', type)
      .del()
      .then(console.log(`Deleted companies_categories: ${toDelete}`))
  ])
}

// RATINGS
export const getMaxMinYearsDividends = async() => {
  const minMax = await knex('dividends')
    .max({ last_year: 'period_year' })
    .min({ first_year: 'period_year' })
    .where('period_year', '>', 0)
    .then(console.log('Get Max and Min years of dividends'))

  const { last_year, first_year } = minMax && minMax.length > 0 ? minMax[0] : [null, null]
  return last_year && first_year ? [...Array(last_year - first_year + 1).keys()].map(x => x + first_year) : []
}
export const getDividendsOverall = async() => {
  const years = await getMaxMinYearsDividends()
  const yearsRange = years || await getMaxMinYearsDividends()
  const usersQueryBuilder = knex('companies as c')
    .column(
      'c.name as name',
      'c.has_mos_index',
      'o.name as otrasl_name'
    )
    // exclude companies without dividends
    .innerJoin(function() {
      this.max('period_year').column('company_id').from('dividends').groupBy('company_id').as('dmax')
    }, 'dmax.company_id', 'c.id')
    .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')

  yearsRange.forEach(y => {
    usersQueryBuilder.modify(yearJoin, y)
  })
  const data = await usersQueryBuilder.then(console.log('Get overall dividends data'))

  const list = data.map(l => {
    const curPaymentYear = new Date().getFullYear() - 1
    const compYears = Object.keys(l).filter(p => yearsRange.includes(Number.parseInt(p))).map(k => Number.parseInt(k))
    const lastCompYear = compYears[compYears.length - 1]
    const offsetYear = lastCompYear > curPaymentYear ? lastCompYear - curPaymentYear : 0
    const curPaymentYearOffset = yearsRange.length - 1 - yearsRange.indexOf(curPaymentYear)
    const last5 = yearsRange.slice(-5 - 1 - curPaymentYearOffset + offsetYear, yearsRange.length - curPaymentYearOffset + offsetYear)
    let skipCheck = true
    let prevVal = 0
    let indStab = 0
    let indGrow = 0
    for (const year of last5) {
      if (skipCheck) {
        prevVal = compYears.indexOf(year) > -1 ? l[year] : 0
        skipCheck = false
      } else {
        if (compYears.indexOf(year) > -1) {
          if (l[year] > 0) { indStab++ }

          if (l[year] > prevVal) { indGrow++ }
          prevVal = l[year]
        } else { prevVal = 0 }
      }
    }
    return Object.assign(l, { indexGrow: indGrow, indexStab: indStab, rating: indGrow + indStab, ratingValue: indGrow + indStab })
  })
  return [years, list]
}
export const getDividendsDohodnost = async() => {
  const curYear = new Date().getFullYear()
  const years = [curYear - 1, curYear, curYear + 1]
  const data = await knex('companies as c')
    .column(
      ' c.name as name',
      'c.has_mos_index',
      'o.name as otrasl_name',
      'p.close',
      'p.date'
    )
    .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')
    .leftJoin('prices as p', function() {
      this.on(knex.raw('p.company_id = c.id and p.date = (select max(date) as date from prices where p.company_id = c.id)'))
    })
    .modify(yearJoin, years[0])
    .modify(yearJoin, years[1])
    .modify(yearJoin, years[2])
    .whereNotNull('p.close')
    .then(console.log('Get overall dividends data'))

  const list = data.map(row => {
    const percent = Math.ceil((row[years[1]] && row[years[1]] > 0 ? row[years[1]] / row.close : (row[years[0]] && row[years[0]] > 0 ? row[years[0]] / row.close : 0)) * 10000) / 100
    const percent2 = Math.ceil((row[years[2]] && row[years[2]] > 0 ? row[years[2]] / row.close : 0) * 10000) / 100
    const percentSum = Math.ceil((percent2 && percent2 > 0 ? percent2 : percent) * 10000) / 100
    return Object.assign(row, { percent: percent, percent2: percent2, percentSum: percentSum })
  }).sort((a, b) => a.percentSum > b.percentSum ? -1 : (b.percentSum > a.percentSum ? 1 : 0))

  let previous = null
  const step = list.length / 10
  list.forEach((l, idx, arr) => {
    if (previous === l.percentSum && previous !== null) {
      Object.assign(l, { rating: arr[idx - 1].rating, ratingValue: l.percentSum })
    } else {
      const fig = Number.parseInt((list.length - idx) / step)
      Object.assign(l, { rating: fig === 10 ? fig : fig, ratingValue: l.percentSum })
    }
    previous = l.percentSum
  })

  return list
}
export const getRatingImpulseGrow = async() => {
  const diffJoin = function(queryBuilder, count, interval, agrFunc, isCurrent) {
    const alias = isCurrent ? 'p' : `p${count}${interval}`
    const selectStr = isCurrent ? `p.close as cur_price` : `p.close - ${alias}.close as diff_${count}${interval === 'YEAR' ? 'y' : 'm'}`
    queryBuilder.leftJoin(`prices as ${alias}`, function() {
      this.on(knex.raw(`${alias}.company_id = c.id and ${alias}.date = (select ${agrFunc}(date) as date from prices where ${alias}.company_id = c.id and date > DATE_SUB(NOW(),INTERVAL ${count} ${interval}))`))
    }).select(knex.raw(selectStr))
  }
  const data = await knex('companies as c')
    .column(
      'c.name as name',
      'c.has_mos_index',
      'o.name as otrasl_name',
      'o.id as otrasl_id',
      'p.close as cur_price',
      'p.date',
      'pm.min_price as min_price',
      'pm.max_price as max_price'
    )
    .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')
    .leftJoin(function() {
      this.max('close as max_price')
        .min('close as min_price')
        .column('company_id')
        .from('prices')
        .whereRaw('date > DATE_SUB(NOW(),INTERVAL 1 YEAR)')
        .groupBy('company_id')
        .as('pm')
    }, 'pm.company_id', 'c.id')
    .modify(diffJoin, 1, 'YEAR', 'max', true)
    .modify(diffJoin, 1, 'YEAR', 'min')
    .modify(diffJoin, 1, 'MONTH', 'min')
    .modify(diffJoin, 3, 'MONTH', 'min')
    .modify(diffJoin, 6, 'MONTH', 'min')
    .whereNotNull('p.close')
    .then(console.log('Get rating impulse'))

  data.sort((a, b) => a.diff_6m > b.diff_6m ? -1 : (b.diff_6m > a.diff_6m ? 1 : 0))

  let previous = null
  const step = data.length / 10
  data.forEach((l, idx, arr) => {
    const diffPerc = (price, diff) => Math.ceil(price !== diff ? diff / (price - diff) * 10000 : 0) / 100
    l.diff_1m_perc = diffPerc(l.cur_price, l.diff_1m)
    l.diff_3m_perc = diffPerc(l.cur_price, l.diff_3m)
    l.diff_6m_perc = diffPerc(l.cur_price, l.diff_6m)
    l.diff_1y_perc = diffPerc(l.cur_price, l.diff_1y)

    if (previous === l.diff_6m && previous !== null) {
      Object.assign(l, { rating: arr[idx - 1].rating, ratingValue: l.diff_6m })
    } else {
      const fig = Number.parseInt((data.length - idx) / step)
      Object.assign(l, { rating: fig === 10 ? fig : fig, ratingValue: l.diff_6m })
    }
    previous = l.diff_6m
  })
  return data
}
export const yearJoin = function(queryBuilder, year) {
  queryBuilder.leftJoin(function() {
    this.sum('payment as sum')
      .column('company_id')
      .from('dividends')
      .groupBy('period_year', 'company_id')
      .where('period_year', year)
      .as(`d${year}`)
  }, `d${year}.company_id`, 'c.id')
    .select(`d${year}.sum as ${year}`)
}

export const saveRatingCoefficients = async(ratingName, coefficientsIds, mainId) => {
  await knex.transaction(async trx => {
    await trx('rating_coefficients')
      .del()
      .where('rating_name', ratingName)

    await trx('rating_coefficients')
      .insert(coefficientsIds.map((c) => ({ rating_name: ratingName, coefficient_id: c, is_main: c === mainId })))
      .then(`Rating coefficients ${coefficientsIds.join(', ')} added`)
  })
}
export const getRatingCoefficients = async(ratingName, useCapitalization) => {
  const coefficientNames = await knex('coefficients_values as cv')
    .distinct('cv.coefficient_id')
    .column('c.name', 'rc.is_main')
    .innerJoin('coefficients as c', 'c.id', 'cv.coefficient_id')
    .innerJoin('rating_coefficients as rc', 'rc.coefficient_id', 'c.id')
    .where('rc.rating_name', ratingName)
    .then(console.log('Get columns of coefficients'))

  const builder = knex('companies as c')
    .column(
      'c.id as company_id',
      'c.name as company_name',
      'c.capitalization',
      'o.name as otrasl',
      'cc.id as coefficient_id',
      'cc.name as coefficient_name',
      'cv.value as coefficient_value',
      'cv.id as coefficient_value_id',
      'cf.id as coefficient_formula_id',
      'cf.value as coefficient_formula_value',
      'cv.date'
    )
    .leftJoin('categories_simple as o', 'c.otrasl_id', 'o.id')
    .leftJoin('coefficients_values as cv', 'cv.company_id', 'c.id')
    .leftJoin('coefficients_formulas as cf', 'cf.id', 'cv.coefficient_formula_id')
    .leftJoin('coefficients as cc', 'cc.id', 'cv.coefficient_id')
    // .whereIn('c.id', coefficientNames.map(c => c.coefficient_id))
    .whereIn('c.id', coefficientNames.map(c => c.coefficient_id))
    .whereIn(['c.id', 'cc.id', 'cv.date'], function() {
      this.select('company_id', 'coefficient_id')
        .max('date as date')
        .from('coefficients_values')
        .groupBy('company_id', 'coefficient_id')
    })

  if (useCapitalization) {
    builder
      .columns(knex.raw('c.issue_size * p.close as capitalization_counted'))
      .leftJoin('prices as p', 'p.company_id', 'c.id')
      .whereIn(['c.id', 'p.date'], function() {
        this.select('company_id')
          .max('date as date')
          .from('prices')
          .groupBy('company_id')
      })
  }

  const data = await builder.then(console.log('Get rating coefficients'))
  // const groupData = fillGroupData(data)
  const groupData = data.reduce((acc, item) => {
    if (!acc[item.company_id]) {
      acc[item.company_id] = {
        company: {
          id: item.company_id,
          name: item.company_name,
          otrasl: item.otrasl
        },
        data: coefficientNames.reduce((res, c) => {
          res[c.coefficient_id] = null // {id: c.coefficient_id, name: c.name, value: null}
          return res
        }, {})
      }
      if (useCapitalization) { acc[item.company_id].company.capitalization = item.capitalization ? item.capitalization : item.capitalization_counted }
    }

    acc[item.company_id].data[item.coefficient_id] = {
      coefficient: {
        id: item.coefficient_id,
        name: item.coefficient_name
      },
      date: item.date,
      value: {
        id: item.coefficient_value_id,
        value: item.coefficient_value,
        formula: item.coefficient_formula_id ? { id: item.coefficient_formula_id, value: item.coefficient_formula_value } : null
      }
    }
    return acc
  }, {})

  return { columns: coefficientNames, data: Object.values(groupData) }
}

export const getRatingBriefcasesDividends = async() => {
  const strategyId = 1
  const builder = knex('companies as c')
    .column('c.id as company_id',
      'c.name as company_name',
      'c.lot_size',
      'c.has_mos_index',
      'o.id as otrasl_id',
      'o.name as otrasl_name',
      'p.close',
      'cb.count as exist_count',
      'rb.lots_to_buy_fact',
      'rb.id as lots_to_buy_fact_id',
      'stn.id as strategy_id',
      'stn.name as strategy_name',
      knex.raw('c.lot_size * p.close as lot_price')
    )
    .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')
    .leftJoin('companies_briefcase as cb', 'c.id', 'cb.company_id')
    .leftJoin('rating_briefcase as rb', 'rb.company_id', 'c.id')
    .innerJoin('companies_strategies as st', 'st.company_id', 'c.id')
    .innerJoin('strategies as stn', 'stn.id', 'st.strategy_id')
    .leftJoin(function() {
      this.from('prices')
        .distinct('company_id')
        .column('date', 'close')
        .orderBy('date', 'asc').as('p')
    }, 'p.company_id', 'c.id')
    .where('st.strategy_id', strategyId)
    .groupBy('c.name')
    .orderBy('c.name')

  return builder
}
export const insertRatingBriefcasesDividends = async(data) => {
  await knex('rating_briefcase')
    .insert({
      company_id: data.company_id,
      lots_to_buy_fact: data.lots_to_buy_fact,
      strategy_id: data.strategy_id
    })
    .then(console.log(`Rating briefcase value added`))
}
export const updateRatingBriefcasesDividends = async(data) => {
  await knex('rating_briefcase')
    .update({
      company_id: data.company_id,
      lots_to_buy_fact: data.lots_to_buy_fact,
      strategy_id: data.strategy_id
    })
    .where({ id: data.to_by_id })
    .then(console.log('Rating briefcase value updated'))
}
export const deleteRatingBriefcasesDividends = async(id) => {
  await knex('rating_briefcase')
    .where('id', id)
    .del()
    .then(console.log(`Rating briefcase value id ${id} deleted`))
}

// COEFFICIENTS
export const getCoefficients = async(ids) => {
  const builder = knex('coefficients as c')
    .column('c.id', 'c.name', 'c.description', 'cf.id as formula_id', 'cf.value as value')
    .leftJoin('coefficients_formulas as cf', 'c.id', 'cf.coefficient_id')
    .orderBy('c.name')

  if (ids) { builder.whereIn('c.id', ids) }

  const data = await builder.then(console.log(`Get coefficients`))

  const groupData = data.reduce((acc, item) => {
    if (!acc[item.id]) { acc[item.id] = { id: item.id, name: item.name, description: item.description, formulas: [] } }
    if (item.formula_id) { acc[item.id].formulas.push({ id: item.formula_id, value: item.value }) }
    return acc
  }, {})
  return Object.values(groupData)
}
export const insertCoefficient = async(coefficient) => {
  await knex.transaction(async trx => {
    const coefficientId = await trx('coefficients')
      .insert({
        name: coefficient.name,
        description: coefficient.description ? coefficient.description : null
      })

    await trx('coefficients_formulas')
      .insert(coefficient.formulas.map((f) => ({ value: f.value, coefficient_id: coefficientId })))
      .then(console.log(`Coefficients ${coefficient.name} added`))
  })
}
export const updateCoefficient = async(coefficient) => {
  await knex.transaction(async trx => {
    const existFormulas = await trx('coefficients_formulas')
      .column('id', 'value')
      .where('coefficient_id', coefficient.id)

    const formulasNew = coefficient.formulas.filter((f) => !f.id)
    const formulasUpdate = coefficient.formulas.filter((f) => existFormulas.find(e => e.id === f.id && e.value !== f.value))
    const formulasDelete = existFormulas.filter((e) => !coefficient.formulas.find(f => f.id === e.id))

    await trx('coefficients_formulas')
      .insert(formulasNew.map((f) => ({ value: f.value, coefficient_id: coefficient.id })))

    for (const f of formulasUpdate) {
      await trx('coefficients_formulas')
        .update({ value: f.value })
        .where({ id: f.id })
    }

    for (const f of formulasDelete) {
      const formulas = await trx('coefficients_formulas').select('id').where({ id: f.id })
      const ids = formulas.map(i => i.id)

      await trx('coefficients_values')
        .del()
        .whereIn('coefficient_formula_id', ids)

      await trx('coefficients_formulas')
        .del()
        .whereIn('id', ids)
    }

    await trx('coefficients')
      .update({
        name: coefficient.name,
        description: coefficient.description ? coefficient.description : null
      })
      .where({ id: coefficient.id })
      .then(console.log(`Coefficients ${coefficient.name} updated`))
  })
}
export const deleteCoefficient = async(id) => {
  await knex.transaction(async trx => {
    await trx('coefficients_values')
      .del()
      .where('coefficient_id', id)

    await trx('coefficients_formulas')
      .del()
      .where('coefficient_id', id)

    await trx('coefficients')
      .where('id', id)
      .del()
      .then(console.log('Coefficients deleted'))
  })
}

export const getCoefficientsValuesDates = async(companyId) => {
  const builder = knex('coefficients_values')
    .distinct('date')
    .orderBy('date')

  if (companyId) { builder.where('company_id', companyId) }

  return builder.then(console.log(`Get coefficient value dates`))
}
export const getCoefficientsValues = async(companyId, date, coefficientId) => {
  const builder = knex('coefficients_values as cv')
    .column(
      'cv.id',
      'cv.value',
      'cv.date',
      'cs.id as coefficient_id',
      'cs.name as coefficient_name',
      'cf.id as formula_id',
      'cf.value as formula'
    )
    .innerJoin('coefficients as cs', 'cv.coefficient_id', 'cs.id')
    .leftJoin('coefficients_formulas as cf', 'cf.id', 'cv.coefficient_formula_id')
    .orderBy('cv.id', 'asc')

  if (companyId) { builder.where('cv.company_id', companyId) }

  if (date) { builder.where('cv.date', date) }

  if (coefficientId) { builder.where('cs.id', coefficientId) }

  const data = await builder.then(console.log('Get coefficient values'))

  const groupData = data.reduce((acc, item) => {
    if (!acc[item.coefficient_id]) {
      acc[item.coefficient_id] = {
        coefficient: { id: item.coefficient_id, name: item.coefficient_name },
        values: {}
      }
    }
    acc[item.coefficient_id].values[item.date] = {
      id: item.id,
      value: item.value,
      formula: item.formula_id ? { id: item.formula_id, value: item.formula } : null
    }
    return acc
  }, {})
  return Object.values(groupData)
}
export const insertCoefficientValue = async(coefficientValue, companyId) => {
  await knex('coefficients_values')
    .insert({
      company_id: companyId,
      date: coefficientValue.date,
      coefficient_id: coefficientValue.coefficient_id,
      coefficient_formula_id: coefficientValue.coefficient_formula_id ? coefficientValue.coefficient_formula_id : null,
      value: coefficientValue.value
    })
    .then(console.log(`Coefficient value ${coefficientValue.coefficient_id} added`))
}
export const updateCoefficientValue = async(coefficientValue) => {
  await knex('coefficients_values')
    .update({
      date: coefficientValue.date,
      coefficient_id: coefficientValue.coefficient_id,
      coefficient_formula_id: coefficientValue.coefficient_formula_id ? coefficientValue.coefficient_formula_id : null,
      value: coefficientValue.value
    })
    .where({ id: coefficientValue.id })
    .then(console.log(`Coefficient value ${coefficientValue.id} updated`))
}
export const deleteCoefficientValue = async(id) => {
  await knex('coefficients_values')
    .where('id', id)
    .del()
    .then(console.log(`Coefficient id ${id} deleted`))
}
export const copyCoefficientValues = async(sourceDate, targetDate, companyId) => {
  await knex.transaction(async trx => {
    const source = await trx('coefficients_values')
      .column('coefficient_id', 'coefficient_formula_id')
      .whereNull('value')
      .andWhere('company_id', companyId)
      .andWhere('date', sourceDate)

    await trx('coefficients_values')
      .insert(source.map((s) => (
        {
          coefficient_id: s.coefficient_id,
          coefficient_formula_id: s.coefficient_formula_id,
          company_id: companyId,
          date: targetDate
        }
      )
      )).then(console.log(`Coefficients data copied from  ${sourceDate} to ${targetDate}`))
  })
}

// BRIEFCACE
export const getBriefcase = async() => {
  return knex('briefcase')
    .column('id', 'fill_up')
    .then(console.log(`Get briefcase value dates`))
}
export const updateBriefcase = async(briefcase) => {
  await knex('briefcase')
    .update({ fill_up: briefcase.fill_up })
    .where({ id: briefcase.id })
    .then(console.log(`Briefcase value updated`))
}
export const getCompanyBriefcases = async(dateFrom = undefined, dateTo = undefined) => {
  const dateFromStr = dateFrom ? `'${dateFrom}'` : 'CURDATE()'
  const dateToStr = dateTo ? `'${dateTo}'` : 'CURDATE()'
  const builder = knex('companies as c')
    .column('c.id as company_id',
      'c.name as company_name',
      'c.tiker as tiker',
      'c.currency',
      'c.lot_size',
      'c.has_mos_index',
      'o.id as otrasl_id',
      'o.name as otrasl_name',
      'p_start.date as date_start',
      'p_start.close as price_start',
      'p_end.date as date_end',
      'p_end.close as price_end',
      'cb.count',
      'stn.id as strategy_id',
      'stn.name as strategy_name',
      'cb.id as id',
      'cb.part_name',
      'cb.type_document',
      'cb.dividends',
      'cb.withdrawal',
      'cb.created_date',
      knex.raw('cb.count * p_start.close as cb_start'),
      knex.raw('cb.count * p_end.close as cb_end')/*,
      knex.raw('cb_end - cb_start as dohodnost'),
      knex.raw('cb_end - cb_start as dohodnost'),
      knex.raw('dohodnost / cb_end as dohodnost_perc')*/

    )
    .leftJoin('categories_simple as o', 'o.id', 'c.otrasl_id')
    .innerJoin('companies_briefcase as cb', 'c.id', 'cb.company_id')
    .innerJoin('strategies as stn', 'stn.id', 'cb.strategy_id')
    .innerJoin(function() {
      this.from('prices')
        .column('company_id', 'close')
        .min('date as date')
        .whereRaw(`date >= (SELECT DATE_ADD(LAST_DAY(DATE_SUB(${dateFromStr}, interval 1 month )), interval 1 day ))`)
        .groupBy('company_id')
        .as('p_start')
    }, 'c.id', 'p_start.company_id')
    .innerJoin(function() {
      this.from('prices')
        .column('company_id', 'close')
        .max('date as date')
        .whereRaw(`date <= (SELECT LAST_DAY(${dateToStr}))`)
        .groupBy('company_id')
        .as('p_end')
    }, 'c.id', 'p_end.company_id')
    .groupBy(['c.name', 'cb.strategy_id'])
    .orderBy('c.name')

  if (dateTo) { builder.where('cb.created_date', '<=', dateTo) }
  return builder
}
export const updateCompanyBriefcase = async(item) => {
  const data = {
    company_id: item.company_id,
    strategy_id: item.strategy_id,
    part_name: item.part_name,
    type_document: item.type_document,
    dividends: typeof item.dividends === 'string' && item.dividends !== '' ? item.dividends.replace(',', '.') : (item.dividends ? item.dividends : null),
    withdrawal: typeof item.withdrawal === 'string' && item.withdrawal !== '' ? item.withdrawal.replace(',', '.') : (item.withdrawal ? item.withdrawal : null),
    count: item.count ? item.count : null
  }
  if (item.id) {
    await knex('companies_briefcase')
      .update(data)
      .where({ id: item.id })
      .then(console.log(`Company briefcase updated`))
  } else {
    await knex('companies_briefcase')
      .insert(data)
      .then(console.log(`Company briefcase added`))
  }

  await knex.raw(
    knex('companies_strategies')
      .insert({ company_id: data.company_id, strategy_id: data.strategy_id })
      .toString()
      .replace('insert', 'INSERT IGNORE')
  )
}

// STRATEGIES
export const getStrategies = async() => {
  return knex('strategies')
    .orderBy('name')
    .then(console.log('Get strategies'))
}

// COMPANY_STRATEGY
export const getCompaniesStrategies = async() => {
  return knex('companies_strategies')
    .column('company_id', 'strategy_id')
    .then(console.log('Get company strategies'))
}

// MIH STRATEGY
export const getMihData = async() => {
  const data = await knex('companies as c')
    .column(
      'c.id as company_id',
      'c.name as name',
      'c.tiker',
      'c.lot_size',
      'p.id as price_id',
      'p.close as price',
      'm.id as id',
      'res.resistance',
      'sup.support',
      'buy.signal_buy',
      'stl.risk_level',
      'm.resistance_id',
      'm.support_id',
      'm.signal_buy_id',
      'm.risk_level_id',
      'm.decision',
      'm.multiply',
      'm.budget',
      'm.lots',
      'm.lot_price',
      'm.important'
    )
    .leftJoin(
      knex('prices as p1')
        .column('p1.id', 'p1.date', 'p1.close', 'p1.company_id')
        .innerJoin(
          knex('prices')
            .column('company_id')
            .max('date as last_date')
            .groupBy('company_id')
            .as('p2'),
          function() {
            this.on('p1.date', 'p2.last_date')
              .andOn('p1.company_id', 'p2.company_id')
          }
        )
        .as('p'),
      function() {
        this.on('p.company_id', 'c.id')
      }
    )
    .innerJoin('companies_strategies as str', 'str.company_id', 'c.id')
    .leftJoin('mih_strategy as m', 'm.company_id', 'c.id')
    .leftJoin('mih_strategy_details as res', 'm.resistance_id', 'res.id')
    .leftJoin('mih_strategy_details as sup', 'm.support_id', 'sup.id')
    .leftJoin('mih_strategy_details as buy', 'm.signal_buy_id', 'buy.id')
    .leftJoin('mih_strategy_details as stl', 'm.risk_level_id', 'stl.id')
    /* .whereNotNull('p.close')*/
    .where('str.strategy_id', 2) // 2 - Mih strategy
    .orderBy([{ column: 'm.important', order: 'desc' }, { column: 'name', order: 'asc' }])
    .then(console.log('Get mih strategy data'))

  const existIds = data.map(p => p.price_id).filter(p => !!p)
  const prevData = await knex('companies as c')
    .column(
      'c.id as company_id',
      'p.close as price'
    )
    .leftJoin(
      knex('prices')
        .column('id', 'company_id', 'close')
        .max('date as date')
        .whereNotIn('id', existIds)
        .groupBy('company_id')
        .as('p'),
      function() {
        this.on('c.id', 'p.company_id')
      })
    /* .whereNotNull('p.close')*/
    .then(console.log('Get mih strategy data'))
  data.forEach(d => {
    const p_prev = prevData.find(p => p.company_id === d.company_id)
    if (p_prev) {
      d['price_prev'] = p_prev.price
      d['price_diff_perc'] = p_prev.price ? (d.price - p_prev.price) / d.price * 100 : null
    }
  })

  return data
}
export const getMihDataDetails = async(strategyId) => {
  return knex('mih_strategy_details')
    .column(
      'id',
      'type',
      'resistance',
      'resistance_avg',
      'support',
      'support_avg',
      'signal_buy',
      'risk_level',
      'trend',
      'trend_phase',
      'volatility',
      'meaning_trading_volume'

    )
    .where('strategy_id', strategyId)
    .then(console.log('Get mih strategy details'))
}
export const updateMihData = async(item) => {
  const correctPrice = (price) => typeof price === 'string' && price !== '' ? price.replace(',', '.') : (price || null)
  const correctForeignId = (val) => val || null
  const data = {
    company_id: item.company_id,
    resistance_id: correctForeignId(item.resistance_id),
    support_id: correctForeignId(item.support_id),
    signal_buy_id: correctForeignId(item.signal_buy_id),
    risk_level_id: correctForeignId(item.risk_level_id),
    multiply: correctPrice(item.multiply),
    budget: correctPrice(item.budget),
    lots: correctPrice(item.lots),
    lot_price: correctPrice(item.lot_price),
    decision: item.decision,
    important: item.important ? item.important : null
  }
  if (item.id) {
    return await knex('mih_strategy')
      .update(data)
      .where({ id: item.id })
      .then(console.log(`Mih strategy row updated`))
  } else {
    return await knex('mih_strategy')
      .insert(data)
      .then(console.log(`Mih strategy row added`))
  }
}
export const updateMihDetailsData = async(item, strategy) => {
  const correctPrice = (price) => typeof price === 'string' && price !== '' ? price.replace(',', '.') : (price || null)
  const data = {
    type: item.type,
    strategy_id: strategy.id,
    resistance: correctPrice(item.resistance),
    resistance_avg: correctPrice(item.resistance_avg),
    support: correctPrice(item.support),
    support_avg: correctPrice(item.support_avg),
    signal_buy: correctPrice(item.signal_buy),
    risk_level: correctPrice(item.risk_level),
    trend: item.trend,
    trend_phase: item.trend_phase,
    volatility: item.volatility,
    meaning_trading_volume: item.meaning_trading_volume
  }
  if (item.id) {
    await knex('mih_strategy_details')
      .update(data)
      .where({ id: item.id })
      .then(console.log(`Mih strategy row updated`))
  } else {
    if (!strategy.id) {
      const insId = await updateMihData({ company_id: strategy.company_id })
      data.strategy_id = insId[0]
    }
    await knex('mih_strategy_details')
      .insert(data)
      .then(console.log(`Mih strategy row added`))
  }
}

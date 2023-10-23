function fillUrl(endpoint, params) {
  let url = `http://localhost:8000/${endpoint}`
  if (params && Object.keys(params).length > 0) {
    url += '?'
    url += Object.keys(params)
      .filter(k => !!params[k])
      .map(k => `${k}=${params[k]}`)
      .join('&')
  }
  return url
}

async function requestWithBody(method, endpoint = '', body = {}, parseResponse = true, params = {}) {
  try {
    const url = fillUrl(endpoint, params)
    const data = await fetch(url, {
      method: method,
      mode: 'cors', // no-cors, *cors, same-origin
      headers: {
        'Content-Type': 'application/json'
      },
      redirect: 'follow', // manual, *follow, error
      body: JSON.stringify(body)
    })
    if (parseResponse) {
      const content = await data.json()
      return content
    }
    return true
  } catch (e) {
    console.error(e.message)
  }
}

export async function getData(endpoint = '', params = {}, parseJsonResponse = true) {
  try {
    const url = fillUrl(endpoint, params)
    const data = await fetch(url)
    const content = parseJsonResponse ? await data.json() : await data.text()
    return content
  } catch (e) {
    console.error(e.message)
  }
}

export async function postData(endpoint = '', body = {}, parseResponse = true, params = {}) {
  return requestWithBody('POST', endpoint, body, parseResponse, params)
}

export async function putData(endpoint = '', body = {}, parseResponse = true, params = {}) {
  return requestWithBody('PUT', endpoint, body, parseResponse, params)
}

export async function patchData(endpoint = '', body = {}, parseResponse = true, params = {}) {
  return requestWithBody('PATCH', endpoint, body, parseResponse, params)
}

export async function deleteData(endpoint = '', params = {}) {
  return requestWithBody('DELETE', endpoint, {}, false, params)
}

export async function getCategoriesSimple(type) {
  return await getData('categories-simple', {
    'type': type
  })
}

export async function getStrategies() {
  return await getData('strategies')
}

export const endpoints = Object.freeze({
  BRIEFCASE: 'briefcase',
  BRIEFCASE_COMPANIES: 'briefcase/companies',
  COMPANIES: 'api/company/',
  COMPANIES_CATEGORIES: 'companies/categories',
  COMPANIES_STRATEGIES: 'companies/strategies',
  DIVIDENDS: 'dividends',
  DIVIDENDS_DATA: 'dividends/data',
  DIVIDENDS_DOHODNOST: 'dividends/dohodnost',
  DIVIDENDS_OVERALL: 'dividends/overall',
  PRICES: 'prices',
  SYNC_LAST: 'sync/last',
  CATEGORIES: 'categories',
  CATEGORIES_SIMPLE: 'categories-simple',
  COEFFICIENTS: 'coefficients',
  COEFFICIENTS_VALUES: 'coefficients/values',
  COEFFICIENTS_VALUES_DATES: 'coefficients/values/dates',
  COEFFICIENTS_VALUES_COPY: 'coefficients/values/copy',
  RATINGS: 'ratings',
  RATINGS_BRIEFCASE: 'ratings/briefcases',
  RATINGS_COEFFICIENTS: 'ratings/coefficients',
  RATINGS_IMPULSE_GROW: 'ratings/impulse-grow',
  REPORTS: 'reports',
  REPORTS_COLUMNS: 'reports/columns',
  REPORTS_VALUES: 'reports/values',
  REPORTS_VALUE: 'reports/value',
  REPORTS_UNITS: 'reports/units',
  STRATEGIES: 'strategies',
  STRATEGIES_MIH: 'strategies/mih',
  STRATEGIES_MIH_DETAILS: 'strategies/mih/details'
})

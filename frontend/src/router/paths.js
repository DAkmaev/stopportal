export default [
  {
    path: '/',
    name: 'Home',
    redirect: {
      name: 'companies'
    }
  },
  {
    path: '/companies',
    name: 'companies',
    component: () => import(`@/components/companies/Companies`)
  },
  {
    path: '/prices',
    name: 'prices',
    component: () => import(`@/components/Prices`)
  },
  {
    path: '/dividends',
    name: 'dividends',
    component: () => import(`@/components/Dividends`)
  },
  {
    path: '/catalogs/balance',
    name: 'catalogBalance',
    component: () => import(`@/components/catalogs/CatalogTree`),
    props: { type: 'balance' }
  },
  {
    path: '/catalogs/piu',
    name: 'catalogPiu',
    component: () => import(`@/components/catalogs/CatalogTree`),
    props: { type: 'piu' }
  },
  {
    path: '/catalogs/dds',
    name: 'catalogDds',
    component: () => import(`@/components/catalogs/CatalogTree`),
    props: { type: 'dds' }
  },
  {
    path: '/catalogs/otrasli',
    name: 'catalogOtrasli',
    component: () => import(`@/components/catalogs/CatalogSimple`),
    props: { type: 'otrasli' }
  }, {
    path: '/catalogs/strategii',
    name: 'catalogStrategii',
    component: () => import(`@/components/catalogs/CatalogSimple`),
    props: { type: 'strategii' }
  }, {
    path: '/catalogs/coefficients',
    name: 'coefficients',
    component: () => import(`@/components/catalogs/Coefficients`),
    props: { type: 'coefficients' }
  },
  {
    path: '/reports',
    name: 'reports',
    component: () => import(`@/components/reports/Reports`)
  },
  {
    path: '/ratings',
    name: 'ratings',
    component: () => import(`@/components/ratings/Ratings`),
    children: [
      {
        path: 'dividends',
        name: 'ratingDividends',
        component: () => import(`@/components/ratings/RatingDividends`)
      },
      {
        path: 'dividends-dohod',
        name: 'ratingDividendsDohod',
        component: () => import(`@/components/ratings/RatingDividendsDohod`)
      },
      {
        path: 'impulse-grow',
        name: 'ratingImpulseGrow',
        component: () => import(`@/components/ratings/RatingImpulseGrow`)
      },
      {
        path: 'debt',
        name: 'ratingDebt',
        component: () => import(`@/components/ratings/RatingByCoefficients`),
        props: { ratingName: 'debt', ratingColumnName: 'Долговая нагрузка' }
      },
      {
        path: 'free-money-flow',
        name: 'ratingFreeMoneyFlow',
        component: () => import(`@/components/ratings/RatingByCoefficients`),
        props: { ratingName: 'freeMoneyFlow', useCapitalization: true }
      },
      {
        path: 'summary',
        name: 'ratingSummary',
        component: () => import(`@/components/ratings/RatingSummary`)
      },
      {
        path: 'briefcase',
        name: 'ratingBriefcase',
        component: () => import(`@/components/ratings/RatingBriefcaseDividends`)
      }
    ]
  },
  {
    path: '/briefcase',
    name: 'briefcase',
    component: () => import(`@/components/Briefcase`)
  },
  {
    path: '/mihstrategy',
    name: 'strategyMih',
    component: () => import(`@/components/strategies/MihStrategy`)
  }
]

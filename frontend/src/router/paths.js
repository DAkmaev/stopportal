export default [
  {
    path: '/',
    name: 'root',
    component: () => import(`@/views/Start`),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import(`@/views/Login`)
      },
      {
        path: 'home',
        name: 'home',
        component: () => import(`@/views/Home`),
        children: [
          {
            path: 'companies',
            name: 'companies',
            component: () => import(`@/components/companies/Companies`)
          },
          {
            path: '/catalogs/strategies',
            name: 'strategies',
            component: () => import(`@/components/catalogs/Strategies`),
            props: { type: 'strategies' }
          },
          {
            path: '/briefcase',
            name: 'briefcaseRoot',
            component: () => import(`@/components/briefcase/BriefcaseRoot`),
            children: [
              {
                path: 'registry',
                name: 'briefcaseRegistry',
                component: () => import(`@/components/briefcase/BriefcaseRegistry`)
              },
              {
                path: 'summary',
                name: 'briefcaseSummary',
                component: () => import(`@/components/briefcase/BriefcaseSummary`)
              }
            ]
          }
        ]
      }
    ]
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
  },
  {
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
    path: '/mihstrategy',
    name: 'strategyMih',
    component: () => import(`@/components/strategies/MihStrategy`)
  }
]

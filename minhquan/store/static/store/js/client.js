const HTTP_CLIENT = {
  sendRequest: function ({ data, url, ...others }) {
    $.ajax({
      method: 'GET',
      url: '/api' + url,
      data: JSON.stringify({
        ...data,
        'csrfmiddlewaretoken': CSRF_TOKEN
      }),
      fail: function (e) {
        alert('failed')
      },
      success: function (result) {
        console.log('result', result)
      },
      ...others,
    })
  }
}

const SERVICES = {
  addToCartRequest: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/add-to-cart/', data, ...others })
  },
  getCoupon: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/get-coupon/', data, ...others })
  },
  searchProduct: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/search-product/', data, ...others })
  },
}
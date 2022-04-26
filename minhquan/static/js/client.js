const HTTP_CLIENT = {
  sendRequest: function ({ data, url, absoluteUrl, absoluteData, ...others }) {
    $.ajax({
      method: 'GET',
      url: absoluteUrl ? absoluteUrl : '/api' + url,
      data: absoluteData ? absoluteData : JSON.stringify({
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
  postRequest: function ({ url, data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url, data, ...others })
  },
  addToCartRequest: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/add-to-cart/', data, ...others })
  },
  getCoupon: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/get-coupon/', data, ...others })
  },
  getProduct: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/get-product/', data, ...others })
  },
}
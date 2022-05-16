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
    HTTP_CLIENT.sendRequest({ method: 'POST', absoluteUrl: '/sale/api/add-to-cart/', data, ...others })
  },
  getCoupon: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', absoluteUrl: '/sale/api/get-coupon/', data, ...others })
  },
  getProduct: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', absoluteUrl: '/sale/api/get-product/', data, ...others })
  },
  getProductsByRule: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', absoluteUrl: '/sale/api/get-product-by-rule/', data, ...others })
  },
  getCustomersByRule: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', absoluteUrl: '/sale/api/get-customer-by-rule/', data, ...others })
  }
}
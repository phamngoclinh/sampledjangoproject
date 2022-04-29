$(function () {
  const $ruleProduct = $('#id_rule_product')
  const $ruleCustomer = $('#id_rule_customer')
  const $ruleOrder = $('#id_rule_order')
  let product_rules = JSON.parse(document.getElementById('product_rules').textContent)
  let customer_rules = JSON.parse(document.getElementById('customer_rules').textContent)
  let order_rules = JSON.parse(document.getElementById('order_rules').textContent)

  const updateProductRules = function (rules) {
    if (rules.category) {
      $('[name=rule_product_category_value]').val(rules.category.in).change()
      if (rules.category.checked === 'on') {
        $('[name=enable_rule_product_category]').prop('checked', true)
      }
    }

    if (rules.name) {
      let rule_product_name_operator = Object.keys(rules.name)[0]
      $('[name=rule_product_name_operator').val(rule_product_name_operator).change()
      $('[name=rule_product_name_value]').val(rules.name[rule_product_name_operator])
      if (rules.name.checked === 'on') {
        $('[name=enable_rule_product_name]').prop('checked', true)
      }
    }

    if (rules.price) {
      let rule_product_price_operator = Object.keys(rules.price)[0]
      $('[name=rule_product_price_operator').val(rule_product_price_operator).change()
      $('[name=rule_product_price_value]').val(rules.price[rule_product_price_operator])
      if (rules.price.checked === 'on') {
        $('[name=enable_rule_product_price]').prop('checked', true)
      }
    }
  }

  const updateCustomerRules = function (rules) {
    if (rules.full_name) {
      let rule_customer_name_operator = Object.keys(rules.full_name)[0]
      $('[name=rule_customer_name_operator').val(rule_customer_name_operator).change()
      $('[name=rule_customer_name_value]').val(rules.full_name[rule_customer_name_operator])
      if (rules.full_name.checked === 'on') {
        $('[name=enable_rule_customer_name]').prop('checked', true)
      }
    }

    if (rules.dob) {
      let rule_customer_dob_operator = Object.keys(rules.dob)[0]
      $('[name=rule_customer_dob_operator').val(rule_customer_dob_operator).change()
      $('[name=rule_customer_dob_value]').val(rules.dob[rule_customer_dob_operator])
      if (rules.dob.checked === 'on') {
        $('[name=enable_rule_customer_dob]').prop('checked', true)
      }
    }

    if (rules.email) {
      let rule_customer_email_operator = Object.keys(rules.email)[0]
      $('[name=rule_customer_email_operator').val(rule_customer_email_operator).change()
      $('[name=rule_customer_email_value]').val(rules.email[rule_customer_email_operator])
      if (rules.email.checked === 'on') {
        $('[name=enable_rule_customer_email]').prop('checked', true)
      }
    }

    if (rules.phone) {
      let rule_customer_phone_operator = Object.keys(rules.phone)[0]
      $('[name=rule_customer_phone_operator').val(rule_customer_phone_operator).change()
      console.log(rules.phone, rule_customer_phone_operator)
      $('[name=rule_customer_phone_value]').val(rules.phone[rule_customer_phone_operator])
      if (rules.phone.checked === 'on') {
        $('[name=enable_rule_customer_phone]').prop('checked', true)
      }
    }
  }

  const updateOrderRules = function (rules) {
    if (rules.amount_total) {
      let rule_order_amount_total_operator = Object.keys(rules.amount_total)[0]
      $('[name=rule_order_amount_total_operator').val(rule_order_amount_total_operator).change()
      $('[name=rule_order_amount_total_value]').val(rules.amount_total[rule_order_amount_total_operator])
      if (rules.amount_total.checked === 'on') {
        $('[name=enable_rule_order_amount_total]').prop('checked', true)
      }
    }
  }

  if (product_rules) {
    console.log('product_rules', product_rules)
    updateProductRules(product_rules)
  } else {
    product_rules = {}
  }

  if (customer_rules) {
    console.log('customer_rules', customer_rules)
    updateCustomerRules(customer_rules)
  } else {
    customer_rules = {}
  }

  if (order_rules) {
    console.log('order_rules', order_rules)
    updateOrderRules(order_rules)
  } else {
    order_rules = {}
  }

  $('.rule-widget').on('change', function () {
    const model = $(this).data('model')
    const field = $(this).data('field')
    let operator = $(this).data('operator')
    let value = $(this).val()
    let operatorSource = $(this).data('operator-source')
    let valueSource = $(this).data('value-source')

    if (valueSource) {
      operator = $(this).val()
      value = $(`[name=${valueSource}]`).val()
    } else if (operatorSource) {
      operator = $(`[name=${operatorSource}]`).val()
      value = $(this).val()
    }

    const $itemParent = $(this).parents('.accordion')

    let isChecked = $(this).is(':checked')

    if ($(this).hasClass('apply-checkbox') && $itemParent.length) {
      let ruleId = $($itemParent)[0].id
      if (ruleId === 'accordion_rule_product') {
        product_rules[field][operator] = value
        if (!isChecked) {
          delete product_rules[field][operator]
        }
        $ruleProduct.val(JSON.stringify(product_rules))
      } else if (ruleId === 'accordion_rule_customer') {
        customer_rules[field][operator] = value
        if (!isChecked) {
          delete customer_rules[field][operator]
        }
        $ruleCustomer.val(JSON.stringify(customer_rules))
      } else if (ruleId === 'accordion_rule_order') {
        order_rules[field][operator] = value
        if (!isChecked) {
          delete order_rules[field][operator]
        }
        $ruleOrder.val(JSON.stringify(order_rules))
      }
    } else if ($itemParent.length) {
      let ruleId = $itemParent[0].id
      if (ruleId == 'accordion_rule_product') {
        product_rules[field] = {}
        product_rules[field][operator] = value
        $ruleProduct.val(JSON.stringify(product_rules))
      } else if (ruleId == 'accordion_rule_customer') {
        customer_rules[field] = {}
        customer_rules[field][operator] = value
        $ruleCustomer.val(JSON.stringify(customer_rules))
      } else if (ruleId == 'accordion_rule_order') {
        order_rules[field] = {}
        order_rules[field][operator] = value
        $ruleOrder.val(JSON.stringify(order_rules))
      }
    }
  })
})
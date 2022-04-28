$(function () {
  const searchInputAgentSelector = '[class$=search_input_widget_agent]'
  const widgetSelector = '[class$=source_value_search_input]'
  const inputSearchSelector = '[class$=search_text]'
  const searchResultSelector = '[class$=search_result]'
  const selectedResultSelector = '[class$=selected_result]'
  const removeSelectedResultSelector = '[class$=remove_selected_result_button]'
  const addFormButtonSelector = '[class$=add_form_button]'

  const triggerWidgetUpdate = function (agent, value, data) {
    let $searchInputAgent = agent
    let $widget = $searchInputAgent.find(widgetSelector)
    $widget.val(value)
    $widget.trigger('change', data)
  }

  const selectResultItem = function (agent, item) {
    let $searchInputAgent = agent
    let $selectedResult = $searchInputAgent.find(selectedResultSelector)
    let $searchResult = $searchInputAgent.find(searchResultSelector)
    let searchFields = $searchInputAgent.data('search_fields').split(',')

    triggerWidgetUpdate($searchInputAgent, item.id, item)

    let searchResult = searchFields.map(function (field) {
      return `<span>${item[field]}</span>`
    }).join('')

    $selectedResult.find('span:first-child').html(searchResult)
    $selectedResult.show()
    $searchResult.hide()
  }

  $(document)
    .on('focus focusout', inputSearchSelector, function () {
      let $searchInputAgent = $(this).parents(searchInputAgentSelector)
      let $searchResult = $searchInputAgent.find(searchResultSelector)

      if ($searchResult.is(':empty')) {
        $searchResult.hide()
      } else {
        $searchResult.show()
      }
    })
    .on('keyup', inputSearchSelector, function () {
      let $searchInputAgent = $(this).parents(searchInputAgentSelector)
      let $searchResult = $searchInputAgent.find(searchResultSelector)
      let $currentForm = $searchInputAgent.parents('form')
      let relatedData = $searchInputAgent.data('related_data')
      let searchKey = $searchInputAgent.data('search_key')
      let searchFields = $searchInputAgent.data('search_fields').split(',')

      $searchResult.empty()
      cacheData = null
      let searchText = $(this).val()
      if (searchText) {
        let requestBody = { [searchKey]: searchText }
        if (relatedData) {
          let relatedDatas = relatedData.split(',')
          relatedDatas.forEach(function (related) {
            requestBody[related] = $currentForm.find(`#id_${related}`).val()
          })
        }
        SERVICES.postRequest({
          absoluteUrl: $searchInputAgent.data('url'),
          headers: { 'X-CSRFToken': "{% csrf_token %}" },
          data: requestBody,
          success: function (result) {
            if (result.success) {
              cacheData = result.data
              result.data.forEach(function (item, index) {
                let searchResult = searchFields.map(function (field) {
                  if (!item[field] || item[field] === 'null')
                    return '<span></span>'
                  return `<span>${item[field]}</span>`
                }).join('')

                let $searchItem = `
                  <li
                    class="list-group-item list-group-item-action search_item"
                    data-cache-data-index="${index}"
                    data-id="${item.id}"
                    data-search-result="${searchResult}"
                  >
                    <span>${searchResult}</span>
                  </li>
                `
                $searchResult.append($searchItem)
                $searchResult.show()
              })

              $searchInputAgent.find('.search_item').on('click', function () {
                let cacheDataIndex = $(this).data('cache-data-index')
                selectResultItem($searchInputAgent, cacheData[cacheDataIndex])
              })
            }
          }
        })
      }
    })

  $(document).on('click', removeSelectedResultSelector, function () {
    let $searchInputAgent = $(this).parents(searchInputAgentSelector)
    let $selectedResult = $searchInputAgent.find(selectedResultSelector)
    triggerWidgetUpdate($searchInputAgent, '', undefined)
    $selectedResult.find('span:first-child').empty()
    $selectedResult.hide()
  })

  $(document).on('click', addFormButtonSelector, function () {
    let $searchInputAgent = $(this).parents(searchInputAgentSelector)
    let $addForm = $(`.${$searchInputAgent[0].id}`)
    $addForm.show()
  })

  $(document).on('submit', '.search_input_add_form', function (e) {
    e.preventDefault()
    let $addForm = $(this)
    let $addFormTemplate = $addForm.parents('.add_form_template')
    let agentId = $addFormTemplate.attr('class').split(' ')[0]
    let $searchInputAgent = $(`#${agentId}`)
    SERVICES.postRequest({
      absoluteData: $addForm.serialize(),
      absoluteUrl: $addForm.attr('action'),
      success: function (result, textStatus) {
        if (result.success) {
          selectResultItem($searchInputAgent, result.data)
          $addFormTemplate.hide()
        } else {
          $addForm.find('.add_form_fields').html(result.form)
        }
      },
      error: function (error, textStatus, errorThrown) {
        console.log(error, textStatus, errorThrown)
      }
    })
  })

  $(document).on('click', '.close_search_input_add_form', function (e) {
    let $addFormTemplate = $(this).parents('.add_form_template')
    $addFormTemplate.hide()
  })
})
angular.module('Wadi.form', [])
.controller 'FormCtrl', ($scope, $state, $log, $http) ->
  $scope.checkLogin = () ->
    $log.info "Checking login status at FormCtrl"
    if not $scope.$parent.checkLogin()
      $state.go('login')
  # $scope.checkLogin() TODO, change
  $http.get 'http://45.55.72.208/wadi/interface/form'
  .success (data) ->
    configureForm(data)



  $scope.simpleParts = []
  $scope.selectedSimpleParts = {}

  $scope.advancedParts = {}
  $scope.selectedAdvancedParts = {}

  configureForm = (data) ->
    tranformValues = (d) ->
      v = d.values
      d.values = _.map(v, (op) ->
        {id: op, label: op}
      )

    $scope.simpleParts = []
    $scope.advancedParts = {}

    $scope.campaign = {
      text:
        arabic: ''
        english: ''
      date:''
      time:''
    }

    for k in ['category']
      $scope.selectedSimpleParts[k] = []
      tranformValues(data[k])
      $scope.simpleParts.push(data[k])
    $log.info "Configured simple: "+JSON.stringify($scope.simpleParts)

    for k in ['customer']
      tranformValues(data[k])
      $scope.selectedAdvancedParts[k] = []
      $scope.advancedParts[k] = data[k]

  formPartial = () ->
    reverseTransform = (v) ->
      _.map(v, (o) ->
        o.id
      )

    result = {}
    for k, v of $scope.selectedSimpleParts
      v = reverseTransform(v)
      result[k] = v

    temp = $scope.selectedAdvancedParts['customer']
    if temp.length == 2 or temp.length == 0
      result['mode'] = 'all'
    else
      result['mode'] = temp[0].id

    $log.debug "Form submission: #{JSON.stringify(result)}"
    result

  $scope.submit = () ->
    result = {}
    result['target_config'] = formPartial()
    result['campaign'] = $scope.campaign
    $log.info "Posting: "+JSON.stringify(result)

    $http.post('http://45.55.72.208/wadi/interface/post', result)
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)

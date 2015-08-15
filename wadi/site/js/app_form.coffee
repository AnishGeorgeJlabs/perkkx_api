angular.module('Wadi.form', [])
.controller 'FormCtrl', ($scope, $state, $log, $http) ->
  $scope.checkLogin = () ->
    $log.info "Checking login status at FormCtrl"
    if not $scope.$parent.checkLogin()
      $state.go('login')
  $scope.checkLogin()
  $http.get 'http://45.55.72.208/wadi/interface/form'
  .success (data) ->
    configureForm(data)

  # ------- Target Configuration --------- #
  $scope.multi = {}
  $scope.single = {}
  $scope.range = {}

  $scope.selectedMulti = {}
  $scope.selectedSingle = {}
  $scope.selectedRange = {}

  configureForm = (mainData) ->
    for data in mainData
      if data.type == 'single'
        $scope.single[data.operation] = {name: data.pretty, values: data.values }
        $scope.selectedSingle[data.operation] = ''
      else if data.type == 'multi'
        $scope.multi[data.operation] = {name: data.pretty, values: data.values }
        $scope.selectedMulti[data.operation] = []
      else if data.type == 'range'
        $scope.range[data.operation] = {name: data.pretty}

  cleanObj = (obj) ->
    _.pick obj, (val, key, o) ->
      val.length > 0

  # ------------------------------------- #

  $scope.campaign =
    text:
      arabic: ''
      english: ''
    date: ''

  $scope.submit = () ->
    resM = cleanObj($scope.selectedMulti)
    resS = cleanObj($scope.selectedSingle)
    resR = cleanObj($scope.selectedRange)
    target_config = _.extend({}, resS, resM, resR)

    dt = moment($scope.campaign.date).format("MM/DD/YYYY HH:mm").split(" ")

    result = { target_config: target_config, campaign_config: {text: $scope.campaign.text, date: dt[0], time: dt[1]} }
    $log.info "Final submission: "+JSON.stringify(result)

    $http.post('http://45.55.72.208/wadi/interface/post', result)
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)

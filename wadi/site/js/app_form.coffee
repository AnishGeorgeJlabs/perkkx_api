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

  $scope.multi = {}
  $scope.single = {}

  $scope.selectedMulti = {}
  $scope.selectedSingle = {}

  configureForm = (mainData) ->
    for data in mainData
      if data.type == 'single'
        $scope.single[data.operation] = {name: data.pretty, values: data.values }
        $scope.selectedSingle[data.operation] = []
      else
        $scope.multi[data.operation] = {name: data.pretty, values: data.values }
        $scope.selectedMulti[data.operation] = []

    $log.info "Singles: "+JSON.stringify($scope.single)
    $log.info "Multi: "+JSON.stringify($scope.multi)


    ###
  $scope.submit = () ->
    result = {}
    result['target_config'] = formPartial()
    result['campaign'] = $scope.campaign
    $log.info "Posting: "+JSON.stringify(result)

    $http.post('http://45.55.72.208/wadi/interface/post', result)
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)

    ###

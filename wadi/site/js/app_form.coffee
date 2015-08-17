angular.module('Wadi.form', [])
.controller 'FormCtrl', ($scope, $state, $log, $http, $modal) ->
  $scope.checkLogin = () ->
    $log.info "Checking login status at FormCtrl"
    if not $scope.$parent.checkLogin()
      $state.go('login')
  $scope.checkLogin()

  $scope.submitting = false

  $http.get 'http://45.55.72.208/wadi/interface/form'
  .success (data) ->
    $scope.loading = false
    configureForm(data)

  # ------- Target Configuration --------- #
  $scope.loading = true
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
      val and val.length > 0

  # ------------------------------------- #

  $scope.campaign =
    text:
      arabic: ''
      english: ''
    datetime: null

  $scope.submit = () ->
    $scope.submitting = true
    resM = cleanObj($scope.selectedMulti)
    resS = cleanObj($scope.selectedSingle)
    resR = cleanObj($scope.selectedRange)
    target_config = _.extend({}, resS, resM, resR)

    dt = moment($scope.campaign.datetime).format("MM/DD/YYYY HH:mm").split(" ")
    $scope.campaign.date = dt[0]
    $scope.campaign.time = dt[1]

    result = { target_config: target_config, campaign_config: $scope.campaign, debug: false}
    $log.info "Final submission: "+JSON.stringify(result)


    $http.post('http://45.55.72.208/wadi/interface/post', result)
    .success (res) ->
      $log.debug "Submission result: "+JSON.stringify(res)
      $scope.submitting = false
      $modal.open(
        controller: ($scope, $modalInstance) ->
          $scope.result = res
          $scope.close = () ->
            $modalInstance.dismiss('ok')
        templateUrl: 'templates/modal_submission.html'
      )


  $scope.reset = () ->
    $scope.selectedMulti = _.mapObject($scope.selectedMulti, () -> [] )
    $scope.selectedSingle = _.mapObject($scope.selectedSingle, () -> '')
    $scope.selectedRange = _.mapObject($scope.selectedRange, () -> '')

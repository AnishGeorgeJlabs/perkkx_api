###
  Wadi sms tool web interface
###

angular.module('Wadi', ['ui.router'])
.config ($stateProvider, $urlRouterProvider) ->
  $stateProvider
  .state('login',
    templateUrl: './templates/view_login.html'
    controller: 'LoginCtrl'
  )
  .state('main',
    templateUrl: './templates/view_main.html'
    controller: 'FormCtrl'
  )

.controller 'MainCtrl', ($scope, $state, $http, $log) ->
  $log.debug "Main executed"
  $state.go('login')

  isLoggedIn = false

  $scope.checkLogin = () -> isLoggedIn

  $scope.login = (username, pass) ->
    $log.debug "Got submission #{username}, #{pass}"
    $http.post "http://45.55.72.208/wadi/interface/login", {
      username: username,
      password: pass
    }
    .success (result) ->
      $log.debug "Got result: #{JSON.stringify(result)}"
      isLoggedIn = result.success
      if isLoggedIn
        $state.go('main')
      else
        alert "Authentication failed"

.controller 'LoginCtrl', ($scope, $log) ->
  $scope.data = {
    username: ''
    password: ''
  }

  $scope.submit = () ->
    $log.debug "Submitting : #{JSON.stringify($scope.data)}"
    $scope.$parent.login($scope.data.username, md5($scope.data.password))
    $scope.data.username = ''
    $scope.data.password = ''

.controller 'FormCtrl', ($scope, $state, $log) ->
  $scope.checkLogin = () ->
    $log.info "Checking login status at FormCtrl"
    if not $scope.$parent.checkLogin()
      $state.go('login')

  $scope.checkLogin()

###
angular.module("Wadi", [])
.controller 'MainCtrl', ($scope, $log, $http) ->
  $scope.data = staticData

  $scope.formdata = {}
  $scope.submit = () ->
    nData = $("#dataForm").serializeObject()
    $log.info("Object mode: "+JSON.stringify(nData))
    $http.post "http://45.55.72.208/wadi/interface/post", nData
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)
###

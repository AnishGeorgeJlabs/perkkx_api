###
  Wadi sms tool web interface
###

angular.module('Wadi', ['ui.router'])
.config ($stateProvider, $urlRouterProvider) ->
  $stateProvider
  .state('login',
    templateUrl: './templates/view_login.html'
  )
.controller 'MainCtrl', ($scope, $state, $http) ->
  $state.go('login')

  isLoggedIn = false

  $state.checkLogin = () -> isLoggedIn

  $state.login = (username, pass) ->
    $http.post "45.55.72.208/interface/wadi/login", {
      username: username,
      password: pass
    }
    .success (result) ->
      isLoggedIn = result.success
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

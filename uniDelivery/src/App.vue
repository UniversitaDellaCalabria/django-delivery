<template>
  <div id="app">
    <img src="https://ds.auth.unical.it/static/images/unical_logo.svg">
    <h4>{{ msg }}</h4>
    <p>Servizio di Approvvigionamento SIM e Router del Campus Universitario.</p>
    <!--<h4>Accedi</h4>-->
    <ul>
      <li><a href="#" target="_blank">
            Accedi
          </a>
      </li>
      <li>
        <a href="#" target="_blank">
            Contatti
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'app',
  data () {
    return {
      msg: 'Welcome to uniDelivery App'
    }
  }
}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #918f90;
  text-decoration: none;
}
</style>

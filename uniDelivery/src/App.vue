<template>
  <div id="app">
    <Header></Header>
        <router-view></router-view>     
    <Footer></Footer>
  </div>
</template>

<script>
import Header from './components/Header'
import Footer from './components/Footer'


export default {
  name: 'app',
  components: {
    Header,
    Footer
  },
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

<style scoped lang="sass">
html, body
  margin: 0
  min-height: 100vh
</style>

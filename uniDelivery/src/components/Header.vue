<template>
  <header>
    <div id="logo">
        <img src="https://ds.auth.unical.it/static/images/unical_logo.svg">
    </div>
    <nav>
      <ul>
        <router-link tag='li' :to="{ name: 'home'}">
          <a>Home</a>
        </router-link>
        <router-link tag='li' :to="{ name: 'cutecat'}">
          <a>Link</a>
        </router-link>
      </ul>
    </nav>
  </header>
</template>


<script>
export default{
  data () {
    return {}
  }
}
</script>

<style scoped lang="sass">
  
</style>

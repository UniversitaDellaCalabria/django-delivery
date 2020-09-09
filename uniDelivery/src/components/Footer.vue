<template>
  <footer>
    <hr>
      <ul>
        <router-link tag='li' :to="{ name: 'home'}">
          <a>Home</a>
        </router-link>
        <router-link tag='li' :to="{ name: 'contacts'}">
          <a>Contatti</a>
        </router-link>
      </ul>
    </div>
  </footer>
</template>

<script>
export default{
  data () {
    return {}
  }
}
</script>


<style scoped lang="scss">
    footer {
        margin-top: 5em;
    }
</style>

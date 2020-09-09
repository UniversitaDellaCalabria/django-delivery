<template>
  <button type="button" @click="goTo">{{ this.pathname }}</button>
</template>

<script>
export default {
  props:{
    pathname: {
      type: String,
      required: true
    }
  },
  methods: {
    goTo() {
      this.$router.push({name: this.pathname})
    }
  }
}
</script>

<style scoped lang="scss">
    button {
        width: 80%;
        color: black;
    }
</style>

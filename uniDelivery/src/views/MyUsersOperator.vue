<template>
  <section class="container">
    <div class="pb-md-5 bd-content clearfix" v-if="campaign.is_active">
        <h2>
            <span style="word-break: break-word;">
                {{ campaign.name }}
            </span>
        </h2>
    </div>

    <div class="alert alert-danger" role="alert" v-else>
        Accesso non consentito.
    </div>

  </section>
</template>

<script>
  export default {
    data: function(){
        return {
            campaign: false
        }
    },
    methods: {
        loadData: function () {
            $.get("http://localhost:8000/api/good_delivery/DeliveryCampaign/" + this.$route.params['campain'], function (response) {
                this.campaign = response;
            }.bind(this));
        }
    },
    created: function () {
        this.loadData();

        setInterval(function () {
            this.loadData();
        }.bind(this), 5000);
    }
  }
</script>

<style scoped lang="sass">

</style>

<template>
  <section class="container">
    <div class="pb-md-5 bd-content clearfix">
        <h2>
            <span style="word-break: break-word;">
                Campagne di consegna attive
            </span>
        </h2>
    </div>
    <!--
    <redirectButton pathname="page_one"></redirectButton>
    <redirectButton pathname="page_two"></redirectButton>
    -->

    <div class="row" v-if="campaigns">
        <div class="col-12 col-lg-4 category-box" v-for="campaign of campaigns">
        <!--start card-->
            <div class="card-wrapper card-space">
                <div class="card card-bg no-after">
                    <div class="card-body">

                        <span class="badge badge-success mb-2" v-if="campaign.is_in_progress">
                            Attiva
                        </span>
                        <span class="badge badge-danger mb-2" v-else>
                            Non attiva
                        </span>
                        <router-link class="read-more" :to="{ name: 'users', params: { campain: campaign.id }}">
                            <h5 class="card-title">{{ campaign.name }}</h5>
                        </router-link>
                        <p class="card-text"></p>
                        <p class="card-text">
                            <b>Data inizio:</b> {{ campaign.date_start }}
                            <br>
                            <b>Data fine:</b> {{ campaign.date_end }}
                            <br>
                            <b>Richiede consenso: </b>
                            <svg class="icon icon-xs">
                                <use xlink:href="/src/assets/svg/sprite.svg#it-check" v-if="campaign.require_agreement"></use>
                                <use xlink:href="/src/assets/svg/sprite.svg#it-close" v-else></use>
                            </svg>
                        </p>
                    </div>
                </div>
            </div>
        <!--end card-->
        </div>
    </div>
    <div class="alert alert-danger" role="alert" v-else>
        Non ci sono campagne di consegna attive.
    </div>

  </section>
</template>

<script>
  import redirectButton from '../components/buttons/redirect_button'

  export default {
    components: {
      redirectButton
    },
    data: function(){
        return {
            campaigns: []
        }
    },
    methods: {
        loadData: function () {
            $.get("http://localhost:8000/api/good_delivery/DeliveryCampaign/", function (response) {
                this.campaigns = response;
            }.bind(this));
        }
    },
    created: function () {
        this.loadData();

        setInterval(function () {
            console.log(this.campaigns);
            this.loadData();
        }.bind(this), 5000);
    }
  }
</script>

<style scoped lang="sass">

</style>

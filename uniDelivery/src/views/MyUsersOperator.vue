<template>
  <section class="container">
    <div class="pb-md-5 bd-content clearfix" v-if="campaign && campaign.is_active">
        <h2>
            <span style="word-break: break-word;">
                {{ campaign.name }}
            </span>
        </h2>

        <vue-good-table
          :columns="columns"
          :rows="rows"/>
    </div>

    <div class="alert alert-danger" role="alert" v-else>
        Accesso non consentito.
    </div>

  </section>
</template>

<script>
import 'vue-good-table/dist/vue-good-table.css'
import { VueGoodTable } from 'vue-good-table';
  export default {
    data: function(){
        return {
            campaign: false,
            users: [],
            columns: [
        {
          label: 'Name',
          field: 'name',
        },
        {
          label: 'Age',
          field: 'age',
          type: 'number',
        },
        {
          label: 'Created On',
          field: 'createdAt',
          type: 'date',
          dateInputFormat: 'yyyy-MM-dd',
          dateOutputFormat: 'MMM do yy',
        },
        {
          label: 'Percent',
          field: 'score',
          type: 'percentage',
        },
      ],
      rows: [
        { id:1, name:"John", age: 20, createdAt: '',score: 0.03343 },
        { id:2, name:"Jane", age: 24, createdAt: '2011-10-31', score: 0.03343 },
        { id:3, name:"Susan", age: 16, createdAt: '2011-10-30', score: 0.03343 },
        { id:4, name:"Chris", age: 55, createdAt: '2011-10-11', score: 0.03343 },
        { id:5, name:"Dan", age: 40, createdAt: '2011-10-21', score: 0.03343 },
        { id:6, name:"John", age: 20, createdAt: '2011-10-31', score: 0.03343 },
      ],
        }
    },
    methods: {
        loadData: function () {
            $.get("http://localhost:8000/api/good_delivery/DeliveryCampaign/" + this.$route.params['campain'], function (response) {
                this.campaign = response;
            }.bind(this));
        },
        getUsers: function () {
            $.get("http://localhost:8000/api/good_delivery/UserDeliveryPoint/" + this.$route.params['campain'], function (response) {
                this.users = response;
            }.bind(this));
        }
    },
    created: function () {
        this.loadData();
        this.getUsers();
        setInterval(function () {
            this.loadData();
            this.getUsers();
        }.bind(this), 5000);
    },
    components: {
        VueGoodTable,
    }
  }
</script>

<style scoped lang="sass">

</style>

<template>
  <div class="twoStateSwitchWrapper">
    <div :class="['sxls', stateInterpreter()]" v-on:click="switchIt">
      <FA-Icon v-if="this.edit" icon="trash-can" class="sxls50 faicon trash" pull="left" v-on:click="removeFn(this.id, this.name)"/>
      <span v-if="!loading" class="sxlsGrow">{{ this.name }}</span>
      <FA-Icon v-if="loading"  icon="cog" class="sxlsGrow fa-spin" style="font-size: 1.6em;"/>
      <FA-Icon v-if="this.edit" icon="pen-to-square" class="sxls50 faicon edit" pull="right" v-on:click="editComponent(this.allMeta)"/>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "TwoStateSwitch",
  props: {
    id: { required: true },
    type: { required: true },
    name: { required: true },
    state: { required: true },
    onAction: { required: true },
    offAction: { required: true },
    edit: { required: true },
    active: { required: true },
    removeFn: { required: true },
    allMeta: { required: true },
    editComponent: { required: true },
  },
  data() {
    return {
      selectedAction: "",
      loading: false,
    };
  },
  methods: {
    stateInterpreter(){
      if(this.state < -1 || this.active == false) return 'disable'
      else if(this.state > 0 && this.active) return 'active'
      else if((this.state == 0 || this.state == -1) && this.active) return 'deactive'
      else return 'deactive'
    },
    switchIt() {
      if(this.stateInterpreter() == "disable") return 0
      if(this.edit===false){
        if(this.stateInterpreter() == "active") this.selectedAction = this.offAction
        else if(this.stateInterpreter() == "deactive") this.selectedAction = this.onAction
        this.loading = true;
         setTimeout(() => { if(this.loading) this.loading=false; },2000);
        this.sendSwitchAction(this.selectedAction)
      }
    },
    async sendSwitchAction(action) {
      await axios
        .post("smart_home_api/aq_api_request", this.$store.getters.authDict({commandline: action}))
        .then((result) => {
          if (result.data.auth) console.log(result.data);
          else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
  watch:{
    state(){
      this.loading = false
    }
  }
};
</script>

<style lang="scss">
.twoStateSwitchWrapper{
  min-width: 100%;

  div{
    width: calc(100% - 30px);
    padding: 30px 10px;
    margin: 5px 0 0 0;
    border-radius: 10px;
  }
}

.sxls{
  display: flex;
  align-items: center;
  width: 100%;
}
.sxls50{
  width: 50px;
  padding: 5px;
}
.sxlsGrow{
  width: 100%;
}
.disable{
  color: #000;
}
</style>
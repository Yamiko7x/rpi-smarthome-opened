<template>
  <div
    class="actionQueueWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <div class="actionsQueue" v-if="render">
      <div v-for="(action, idx) in this.actions" :key="idx">
        <FA-Icon v-if="idx!=0"
          icon="angles-down"
          class="symbolIcon"
        />
        <AutoComponent :compoDict="action" :idx="idx" :rmAction="rmAction" :moveAction="moveAction"/>
      </div>
      <FA-Icon v-if="idx!=0"
        icon="plus"
        :class="['addIcon', this.actionIsEmpty() ? 'borderRadius' : '']"
        @click="closeSearchFns()"
      />
    </div>

    <Teleport to="body" v-if="this.searchFns">
      <SearchActionTemplate :closeEvent="closeSearchFns" :actions="this.actions" :rerender="rerender" />
    </Teleport>
  </div>
</template>

<script>
export default {
  name: "ActionQueue",
  props: {
    actions: { required: true },
  },
  data() {
    return {
      showView: false,
      searchFns: false,
      render: true,
    };
  },
  watch: {
  },
  methods: {
    rerender(){
      this.render=false;
        setTimeout(() => {
          this.render = true;
        }, 100);
    },
    rmAction(idx){
      console.log(idx)
      if(idx == 0) this.actions.shift()
      else this.actions.splice(idx, idx)
      this.rerender()
    },
    moveAction(idx, direct){
      console.log(!this.$store.state.fnsDictRouls[this.actions[idx].fn].basic)
      if(idx > 0  && direct == "down"){ /* down means less index in list */
        let tmp = this.actions[idx-1]
        this.actions[idx-1] = this.actions[idx]
        this.actions[idx] = tmp
        this.rerender()
      }else if(idx < this.actions.length - 1  && direct == "up"){
        let tmp = this.actions[idx+1]
        this.actions[idx+1] = this.actions[idx]
        this.actions[idx] = tmp
        this.rerender()
      }
    },
    closeSearchFns(){
      this.searchFns = !this.searchFns;
    },
    actionIsEmpty(){
      if(this.actions) {
        if(this.actions.length == 0) return true;
      } else return true;
      return false;
    },
  },
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {
    SearchActionTemplate: require("@/components/actions_components/SearchActionTemplate.vue").default,
  },
};
</script>

<style lang="scss" scoped>
.actionQueueWrapper {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: auto;
  width: 100%;

  .actionsQueue{
    width: 100%;
    margin: 2px auto;
  }
  
  .symbolIcon, .addIcon{
    width: 20%;
    padding-bottom: 5px;
    color: #000;
    font-size: 1.2em;
    background-color: #fff;
    box-shadow: 0px 2px 3px rgba(0,0,0,0.2);
    border-radius: 0 0 10px 10px;
  }
  .borderRadius{
    border-radius: 10px;
  }
  .addIcon{
    font-size: 1.5em;
    padding-top: 10px;
    transition: .1s;
    background-color: rgb(102, 173, 102);
    color: #fff;
  }
  .addIcon:hover{
    background-color: rgb(143, 226, 143);
    cursor: pointer;
  }
}

</style>
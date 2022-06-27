<template>
  <div class="autoComponentWrapper" :class="[showView ? 'showView' : 'hideView']">
    
    <div class="menuBar">
      <FA-Icon
        icon="circle-question"
        class="menuIcon"
        @click="addDesc()"
      />
      <FA-Icon
        icon="chevron-down"
        class="menuIcon"
        @click="moveAction(this.idx, 'up')"
      />
      <FA-Icon
        icon="chevron-up"
        class="menuIcon"
        @click="moveAction(this.idx, 'down')"
      />
      <FA-Icon
        icon="trash"
        class="menuIcon"
        @click="rmAction(this.idx)"
      />
      {{this.idx}}
    </div>
    
    <table v-if="this.compoRules">
      <tr>
        <td>Funkcja</td>
        <td>{{ this.compoDict.fn }} ({{this.compoRules.tip}})</td>
      </tr>
      
      <tr v-for="(rules, idx) in this.compoRules.rules" :key="idx">
        <td v-if="rules.component!='actionQueue'">{{rules.label}}</td>
        <td v-if="rules.component=='inputText'">        <InputText   :rules="rules" :compoDict="this.compoDict" /></td>
        <td v-else-if="rules.component=='inputNumber'"> <InputNumber :rules="rules" :compoDict="this.compoDict" /></td>
        <td v-else-if="rules.component=='select'">      <InputSelect :rules="rules" :compoDict="this.compoDict" /></td>
        <td v-else-if="rules.component=='actionQueue'" class="actionQueueBox" colspan="100%">
            <div class="actionQueueLabel">{{ rules.label }}</div>
            <ActionQueue :actions="this.compoDict[rules.prop]" />
        </td>
        <div v-else>{{ this.compoDict }}</div>
      </tr>

    </table>
    <table v-else>
      <tr>
        <td>Component Error</td>
        <td>Nie znaleziono funkcji: {{ this.compoDict.fn }}. Sprawdź czy jej nazwa na serwerze nie została zmieniona.</td>
      </tr>
      <tr>
        <td>Zmień funkcję</td>
        <td><input type="text" v-model="this.compoDict.fn"></td>
      </tr>
    </table>
    
    <Teleport v-if="popupBoxMessage" to="body">
      <PopupBox :closeEvent="closeEvent" :messages="popupBoxMessage" />
    </Teleport>
  </div>
</template>

<script>
export default {
  name: "AutoComponent",
  components: {
    InputText: require("@/components/atomic_components/InputText.vue").default,
    InputNumber: require("@/components/atomic_components/InputNumber.vue").default,
    InputSelect: require("@/components/atomic_components/InputSelect.vue").default,
  },
  props: {
    compoDict: { required: true },
    idx: { required: true },
    rmAction: { required: true },
    moveAction: { required: true },
  },
  data() {
    return {
      showView: false,
      compoRules: this.$store.state.fnsDictRouls[this.compoDict.fn] ? this.$store.state.fnsDictRouls[this.compoDict.fn] : null,
      popupBoxMessage: null,
    };
  },
  watch: {},
  methods: {
    addDesc(){
      this.popupBoxMessage = [this.compoDict.fn + " (" + this.compoRules.tip + ")", this.compoRules.desc];
    },
    closeEvent(){
      this.popupBoxMessage = null;
    }
  },
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
};
</script>

<style lang="scss" scoped>
.autoComponentWrapper {
  width: calc(100%);
  height: 100%;
  background-color: #fff;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
  overflow-x: auto;
  
  table {
    /* padding: 10px 10px 0px 10px; */
    width: 100%; 
    padding: 5px;
    padding-top: 0;
    font-size: 1.2em;
    text-align: left;

    td {
      padding: 0px 15px 0px 5px;
    }

    input, select {
      padding: 5px 15px;
      margin: 0;
      box-shadow: none;
    }
    ::placeholder {
      opacity: 0.4;
    }

    .actionQueueBox{
      border-radius: 6px;
      padding: 10px;
      border: 0.15em dotted #999;
      text-align: center;

      .actionQueueLabel{
      width: calc(100% - 20px);
        padding: 10px;
        box-shadow: 1px 1px 4px rgba(0, 0, 0, 0.2);
      }
    }

    @media only screen and (max-width: 600px) {
      input, select {
        width: 55vw;
      }
    }
  }

  .menuBar{
    display: flex;
    justify-content: right;
    margin: 0;
    margin-right: 10px;
    margin-top: 10px;

    .menuIcon{
      font-size: 1.2em;
      margin: 0px 8px;
      transition: .1s;
    }
    .menuIcon:hover{
      color: rgb(253, 99, 94);
      cursor: pointer;
    }
  }

  .questionIcon:hover{
    cursor: pointer;
  }
}
@media only screen and (max-width: 600px) {
}
</style>
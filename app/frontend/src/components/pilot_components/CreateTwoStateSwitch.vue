<template>
  <div class="createTwoStateSwitchWrapper">
    <div class="switchBody">
      <h2>
        ID: {{ this.compDict.id ? this.compDict.id : 'xx' }} - {{ this.compDict.type }} 
      </h2>
      <h2>Stan: {{ this.compDict.state == -1 ? 'Niedostępny' : this.compDict.state ? 'Włączony' : 'Wyłączony'}}</h2>
      <h2>{{ this.toggle ? 'Widget aktywny' : 'Widget nieaktywny' }}</h2>
      <h2>
        <FA-Icon :icon="toggleIcon" :class="['toggleIconButton', this.toggle ? 'factive' : 'fdeactive']" v-on:click="this.toggle = !this.toggle"/>
      </h2>
      <input type="text" v-model="inputName" placeholder="Nazwa przełącznika"> 
      <div>
        <input class="withIconSpace" type="text" v-model="inputOnAction" placeholder="start/stop action_id (przełącznik włączony)">
        <FA-Icon class="searchIcon" icon="magnifying-glass" />
      </div>
      <div>
        <input class="withIconSpace" type="text" v-model="inputOffAction" placeholder="start/stop action_id (przełącznik wyłączony)">
        <FA-Icon class="searchIcon" icon="magnifying-glass" />
      </div>
      <div class="inGroup">
        <select v-model="choosedWatcher">
          <option value="vars">Obserwuj zmienną</option>
          <option value="gpio">Obserwuj GPIO</option>
          <option value="work">Obserwuj akcję</option>
          <option value="custom">Reguła własna</option>
        </select>
        <input type="text" v-model="inputWatcher" :placeholder="choosedWatcherPlaceholder" >
      </div>
      <button @click="sendEditedWidgetDict">{{this.compDict.id ? 'Aktualizuj widget' : 'Zapisz widget'}}</button>
      <button class="cancel" @click="closeEvent('editWidget')">Anuluj</button>
      <!-- <button @click="show">Porównaj</button> -->
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "CreateTwoStateSwitch",
  props: {
    compDict: {required: true, },
    closeEvent: { required: true },
  },
  data() {
    return {
      choosedWatcher: this.compDict.watch_type ? this.compDict.watch_type : 'vars',
      watchOption: {vars:'action_id var_id', gpio:'factory_alias gpio', work:'action_id'},
      choosedWatcherPlaceholder: 'action_id var_id',
      toggle: this.compDict.active,
      toggleIcon: this.compDict.active ? 'toggle-on' : 'toggle-off',

      inputName: this.compDict.name,
      inputOnAction: this.compDict.on_action,
      inputOffAction: this.compDict.off_action,
      inputWatcher: this.compDict.watch_path,
    };
  },
  methods: {
    createNewDict(){
      return {active: (typeof this.toggle) === 'undefined' ? false : this.toggle,
              id: this.compDict.id ? this.compDict.id : -1,
              name: this.inputName ? this.inputName : 'New switch',
              off_action: this.inputOffAction ? this.inputOffAction : '',
              on_action: this.inputOnAction ? this.inputOnAction : '',
              type: 'two_state_switch',
              watch_path: this.inputWatcher ? this.inputWatcher : '',
              watch_type: this.inputWatcher ? this.choosedWatcher : 'custom'}
    },
    show(){
      console.log(this.compDict)
      console.log(this.createNewDict)
    },
    async sendEditedWidgetDict() {
      await axios
        .post("pilot_api/editWidget", this.$store.getters.authDict({widgetDict: this.createNewDict()}))
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            console.log(result.data);
            this.closeEvent('editWidget')
          }
          else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);
        });
    },
    
  },
  watch:{
    choosedWatcher(){
      this.choosedWatcherPlaceholder = this.watchOption[this.choosedWatcher]
    },
    toggle(){
      if(this.toggle) this.toggleIcon = 'toggle-on'
      else this.toggleIcon = 'toggle-off'
    }
  },
  create(){
    this.choosedWatcherPlaceholder = this.watchOption[this.choosedWatcher]
  }
};
</script>

<style lang="scss" scoped>
.createTwoStateSwitchWrapper{
  .switchBody{
    width: 90%;
    min-height: 300px;
    border-radius: 30px;
    padding: 30px 0;
    margin: auto;

    h2{
      padding-bottom: 15px;
      margin: 0;
      text-align: center;
    }

    input, select{
      width: calc(100% - 40px);
      padding: 10px 15px;
      box-shadow: none;
      border-bottom: 2px solid rgba(0, 0, 0, 0.3);
      border-radius: 10px;
    }
    .withIconSpace{
      width: 85%;
    }
    @media only screen and (max-width: 600px) {
      .withIconSpace{
        width: 75%;
      }
    }
    
    select{
      width: calc(100% - 10px);
    }
    .inGroup{
      width: calc(100% - 20px);
      margin-left: 10px;
      padding-left: 5px;
      border-left: 5px solid rgba(0, 0, 0, 0.3);
      border-radius: 10px;
     
      input, select{
        border-radius: 0 0 10px 0;
      }
    }

    input:focus, select:focus{
      border-bottom: 2px solid rgba(84, 149, 192, 1);;
    }

    button{
      margin-top: 15px;
      width: 50%;
    }
  }
  
  .searchIcon{
    padding: 0px 10px;
    font-size: 1.3em;
    transition: .1s;
    color: rgba(109, 109, 109, 1);
  }
  .searchIcon:hover{
    color: rgba(84, 149, 192, 1);
    cursor: pointer;
  }

  .toggleIconButton{
    margin: 0 0 -0.12em 10px; 
    font-size: 1.3em; 
    transition: 0.2s;
  }
}

</style>
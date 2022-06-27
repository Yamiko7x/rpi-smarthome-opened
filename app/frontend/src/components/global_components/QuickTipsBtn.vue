<template>
  <div class="quickListBtnWrapper">
      <div class="btn-quickAccess" @click="displayQuickList()">
        <FA-Icon icon="folder-tree" class="faicon"/>
      </div>
      <Teleport to="body">
        <QuickListPanel :class="[this.$store.state.quickPanel ? 'display' : 'hide']">
          <div class="btn-refresh" @click="reloadLists()">
            <FA-Icon icon="arrows-rotate" class="faicon"/>
          </div>
          <div class="mobileMarginTop"></div>
          <details>
              <summary>Actions {{ Object.keys(this.actionsDict).length }}</summary>
              <details v-for="action in actionsDict" :key="action.meta.action_id">
                <summary>
                  <FA-Icon v-if="this.workingActions.includes(action.meta.action_id)" icon="cog" class="fa-spin" style="font-size: 0.8em; margin-right: 10px;"/>
                  <b>{{ action.meta.action_id }}</b> "{{ action.meta.name }}"
                </summary>
                <table>
                  <tr v-if="this.workingActions.includes(action.meta.action_id)">
                    <td><b>working</b></td>
                    <td><b>true</b></td>
                  </tr>
                  <tr v-for="(metaVal, metaKey) in action.meta" :key="metaKey">
                    <td @click="this.copyToClipboard(null,action.meta.action_id)">{{metaKey}}</td>
                    <td @click="this.copyToClipboard(null,action.meta.action_id)"><b>{{metaVal}}</b></td>
                  </tr>
                </table>
            </details>    
          </details>
          
          <hr>
           <details>
              <summary>Vars {{ Object.keys(this.varsDict).length }}</summary>
              <details v-for="(varsVal, varsKey) in varsDict" :key="varsKey">
                <summary><b>Var:</b> {{ varsKey }}</summary>
                <table>
                  <tr v-for="(varVal, varKey) in varsVal" :key="varKey">
                    <td>{{varKey}}</td>
                    <td><b>{{varVal}}</b></td>
                  </tr>
                </table>
              </details>   
          </details>
          
          <hr>
           <details>
              <summary>Working actions {{ this.workingActions.length }}</summary>
              <div v-for="wa in workingActions" :key="wa">
                <p>{{wa}}</p>
              </div> 
          </details>
          
          <hr>
           <details>
              <summary>To stop actions {{ this.toStopActions.length }}</summary>
              <div v-for="tsa in toStopActions" :key="tsa">
                <p>{{tsa}}</p>
              </div> 
          </details>

          <hr>
           <details>
              <summary>Functions {{ Object.keys(this.fnsDict).length }}</summary>
                <table>
                  <tr v-for="(fnVal, fnKey) in this.fnsDict" :key="fnKey">
                    <td @click="this.copyToClipboard(fnVal)"><b>{{fnKey}}</b></td>
                    <td @click="this.copyToClipboard(fnVal)">
                      {{fnVal.template}}
                      <br>return: {{fnVal.return}}
                      <br>import: {{fnVal.import}}</td>
                  </tr>
                </table>
          </details>
          
          <!-- TODO: Add factorys list -->
          <!-- TODO: Add GPIO list -->

        </QuickListPanel>
      </Teleport>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "QuickListBtn",
  data() {
    return {
      actionsDict: {},
      workingActions: [],
      toStopActions: [],
      varsDict: {},
      fnsDict: {},
    };
  },
  methods: {
    copyToClipboard(vDict=null, text=null){
      if(vDict){
        text = vDict.template
        if(this.$route.name=='pilot') text = vDict.import + '.' + text;
      }

      if(vDict || text){
        navigator.clipboard.writeText(text)
        this.$store.dispatch("addMsg", {
          type: "success",
          msg: "Skopiowano: " + text,
        });
        this.$store.state.quickPanel = false
      }
    },
    async loadAllActions() {
      await axios
        .post("actions_api/getAllActionsDict", this.$store.getters.authDict())
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.actionsDict = result.data.actions_dict;
            this.workingActions = result.data.working_actions_ids;
            this.toStopActions = result.data.to_stop_actions;
            this.varsDict = result.data.vars_dict;
            this.fnsDict = result.data.fns_dict;
            }
          else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    displayQuickList() {
      this.$store.state.quickPanel = !this.$store.state.quickPanel
      if(this.$store.state.quickPanel) {
        this.loadAllActions()
      }
    },
    reloadLists() {
      this.loadAllActions()
    },
  },
  components: {
    QuickListPanel: require("@/components/global_components/QuickListPanel.vue").default,
  },
};
</script>

<style lang="scss" scoped>
$quickListBtn-size: 40px;

.display{
  display: initial;
}
.hide{
  display: none;
}

.quickListBtnWrapper {
  position: fixed;
  bottom: calc(85% - 70px);
  right: 0;
  z-index: 100;
}
@media only screen and (max-width: 600px) {
  .quickListBtnWrapper {
  bottom: calc(50% - 70px);
  }
}

.btn-refresh{
  position: fixed;
  bottom: calc(85% - 110px);
  right: 50px;

  .faicon{
    font-size: 1.4em;
    padding: 15px;
    border-radius: 50px;
    margin: 10px;
    background-color: rgb(84, 149, 192);
    color: #fff;
  }
  .faicon:hover {
    cursor: pointer;
    background-color: rgb(27, 77, 110);
  }
}

@media only screen and (max-width: 600px) {
  .btn-refresh{
    position: fixed;
  bottom: calc(50% - 110px);
    right: 50px;
  }
}

details{
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 10px;
  font-size: 18px;
  border: solid 3px rgba(200, 200, 200, 0);
  border-left: solid 3px rgba(200, 200, 200, 1);
  transition: 0.1s;

  td{
    padding-left: 15px;
  }
}
details:hover, details:focus{
  cursor: pointer;
  box-shadow: 1px 1px 4px rgba(0, 0, 0, 0);
  border: solid 3px rgba(84, 149, 192, 1);
}

.mobileMarginTop{
  min-height: 0;
  max-height: 0;
}
@media only screen and (max-width: 600px) {
  .mobileMarginTop {
    min-height: 50vh;
    max-height: 50vh;
    margin: 20px;
    background-color: rgb(236, 236, 236);
  }
}
</style>
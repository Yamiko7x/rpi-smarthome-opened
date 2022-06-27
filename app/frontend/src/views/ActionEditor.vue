<template>
  <div
    class="actionEditorWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <div v-if="display" class="layout">
      <div v-if="this.actionDict">
        <!-- {{ this.actionDict }} <br /> <br> -->
        <!-- {{ this.actionDict.meta }} <br /> -->
        <!-- {{ this.actionDict.actions }} <br /> <br> -->
      </div>
      <!--  {{ this.workingAction }} <br> -->
      <table v-if="this.actionDict">
        <tr>
          <td>working</td>
          <td>
            <FA-Icon
              v-if="this.workingAction"
              icon="cog"
              class="fa-spin"
              style="margin: 0 5px"
            />
            <FA-Icon
              v-if="!this.workingAction"
              icon="ban"
              class=""
              style="margin: 0 5px"
            />
            {{ this.workingAction ? "Akcja w toku" : "Nie uruchomiono" }}
          </td>
        </tr>
        <tr>
          <td>action_id</td>
          <td>
            <input
              v-if="this.action_id == -1"
              type="text"
              v-model="this.actionDict.meta.action_id"
              :class="[
                this.uniqActionID() ? 'borderLeftGreen' : 'borderLeftRed',
              ]"
              placeholder="Niepowtarzalne ID"
            />
            {{ this.action_id != -1 ? this.actionDict.meta.action_id : "" }}
          </td>
        </tr>
        <tr>
          <td>name</td>
          <td>
            <input
              type="text"
              v-model="this.actionDict.meta.name"
              :class="[
                this.actionDict.meta.name != ''
                  ? 'borderLeftGreen'
                  : 'borderLeftRed',
              ]"
              placeholder="Nazwa własna"
            />
          </td>
        </tr>
        <tr>
          <td>active</td>
          <td>
            <FA-Icon
              v-if="this.actionDict.meta.active"
              icon="toggle-on"
              style="margin: 0 5px"
              class="factive"
              @click="this.actionDict.meta.active = false"
            />
            <FA-Icon
              v-if="!this.actionDict.meta.active"
              icon="toggle-off"
              style="margin: 0 5px"
              class="fdeactive"
              @click="this.actionDict.meta.active = true"
            />
          </td>
        </tr>
        <tr>
          <td>autostart</td>
          <td>
            <FA-Icon
              v-if="this.actionDict.meta.autostart"
              icon="toggle-on"
              style="margin: 0 5px"
              class="factive"
              @click="this.actionDict.meta.autostart = false"
            />
            <FA-Icon
              v-if="!this.actionDict.meta.autostart"
              icon="toggle-off"
              style="margin: 0 5px"
              class="fdeactive"
              @click="this.actionDict.meta.autostart = true"
            />
          </td>
        </tr>
        <tr>
          <td>Start/Stop</td>
          <td>
            <FA-Icon
              v-if="this.loading"
              icon="cog"
              class="fa-spin"
              style="margin: 0 5px"
            />
            <button
              v-if="!this.loading"
              :class="[this.workingAction ? 'cancel' : 'add']"
              @click="
                [
                  this.workingAction
                    ? sendAction('stop ' + this.actionDict.meta.action_id)
                    : sendAction('start ' + this.actionDict.meta.action_id),
                ]
              "
            >
              {{ this.workingAction ? "Zatrzymaj akcję" : "Uruchom akcję" }}
            </button>
          </td>
        </tr>
      </table>

      <div class="buttonsBar">
        <button @click="saveAction()">
          {{ this.action_id == -1 ? "Zapisz akcję" : "Aktualizuj akcję" }}
        </button>
        <button class="cancel" @click="this.$router.push('/actions')">
          Anuluj
        </button>
      </div>

      <ActionQueue
        v-if="this.actionDict != null"
        :actions="this.actionDict.actions"
      />
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "ActionEditor",
  data() {
    return {
      display: true,
      action_id: this.$route.params.action_id,
      showView: false,
      actionDict: null,
      workingAction: false,
      loading: false,
      allActionsIDs: [],
      fnsDict: null,
      factoryList: [],
    };
  },
  watch: {},
  methods: {
    uniqActionID() {
      return (
        !this.allActionsIDs.includes(this.actionDict.meta.action_id) &&
        this.actionDict.meta.action_id != ""
      );
    },
    async getFnsDict() {
      await axios
        .post("actions_api/getSimpleFnsDict", this.$store.getters.authDict())
        .then((result) => {
          if (result.data.auth) {
            this.$store.state.fnsDictRouls = result.data.fns_dict;
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);
        });
    },
    async getFactoryList() {
      await axios
        .post("actions_api/getFactoryList", this.$store.getters.authDict())
        .then((result) => {
          if (result.data.auth) {
            console.log(result.data.factory_list)
            this.factoryList = result.data.factory_list;
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);
        });
    },
    async sendAction(action) {
      this.loading = true;
      await axios
        .post(
          "smart_home_api/aq_api_request",
          this.$store.getters.authDict({ commandline: action })
        )
        .then((result) => {
          if (result.data.auth) {
            console.log(result.data);
            setTimeout(() => {
              this.loadActionsByID();
              this.loading = false;
            }, 1000);
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);
        });
    },
    async loadActionsByID() {
      if (this.action_id == -1) {
        this.actionDict = {
          actions: [],
          meta: { action_id: "", active: false, autostart: false, name: "" },
        };
        return false;
      }
      await axios
        .post(
          "actions_api/getActionDictByID",
          this.$store.getters.authDict({ action_id: this.action_id })
        )
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.actionDict = result.data.action_dict;
            this.workingAction = result.data.working;
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    async loadAllActionsIDs() {
      await axios
        .post("actions_api/getAllActionsIDs", this.$store.getters.authDict())
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.allActionsIDs = result.data.all_actions_ids;
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    async saveAction() {
      if (this.action_id == -1) {
        if (this.actionDict.meta.action_id == "") {
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Należy uzupełnić action_id",
          });
          return false;
        } else if (!this.uniqActionID()) {
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Podane action_id już istnieje",
          });
          return false;
        }
      }
      if (this.actionDict.meta.name == "") {
        this.$store.dispatch("addMsg", {
          type: "danger",
          msg: "Należy uzupełnić nazwę",
        });
        return false;
      }
      await axios
        .post(
          "actions_api/saveActionDict",
          this.$store.getters.authDict({
            action_id: this.action_id,
            action_dict: this.actionDict,
          })
        )
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
            
            this.display = false;
            setTimeout(() => {
              this.display = true;
            }, 100);

          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
  },
  created() {
    this.$store.state.goto = '/actions'
    /* console.log(this.action_id); */
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
    this.getFactoryList()
    this.getFnsDict();
    this.loadAllActionsIDs();
    this.loadActionsByID();
  },
  components: {},
};
</script>

<style lang="scss" scoped>
.actionEditorWrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 0;

  .layout{
    width: calc(100% - 40px);
    max-width: 1000px;
    margin: 20px;
  }
  @media only screen and (max-width: 600px) {
    .layout {
      width: 100%;
      margin: 0;
    }
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: #fff;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
    overflow-x: auto;

    tr {
      overflow-x: auto;
    }

    td,
    th {
      text-align: left;
      padding: 8px;
      padding-left: 15px;
      font-size: 1.2em;
    }
    .actionBtn {
      text-align: center;
      padding: 5px 15px;
      margin: 0;
    }
  }
  ::placeholder {
    opacity: 0.4;
  }

  @media only screen and (max-width: 600px) {
    input {
      width: 55vw;
    }
  }

  .buttonsBar {
    width: 100%;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);

    button {
      font-size: 1.1em;
      width: 50%;
      border-left: 1px solid #fff;
      border-right: 1px solid #fff;
    }
  }
}
</style>
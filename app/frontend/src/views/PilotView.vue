<template>
  <div class="pilot-wrapper" :class="[showView ? 'showView' : 'hideView']">
    <!-- TODO: css bug with missing component -->
    <div>
      Refresh Time:
      <span v-if="this.editRefreshTime">
        <input
          type="number"
          min="250"
          style="width: 100px"
          v-model="this.$store.state.refreshWidgetDelay"
        />
        <FA-Icon icon="check" class="icon" @click="this.saveRefreshTime()" title="Zapisz"/>
      </span>
      <span v-else>
        {{ this.$store.state.refreshWidgetDelay }}ms
        <FA-Icon icon="pen-to-square" class="icon" @click="this.editRefreshTime = true" title="Edytuj"/>
      </span>
    </div>
    <div class="pilotContainer">
      <div v-for="widget in widgets" :key="widget.id">
        <TwoStateSwitch
          v-if="widget.type == 'two_state_switch'"
          :id="widget.id"
          :type="widget.type"
          :name="widget.setname"
          :state="widget.state"
          :onAction="widget.on_action"
          :offAction="widget.off_action"
          :edit="this.edit"
          :active="widget.active"
          :removeFn="removeWidget"
          :allMeta="widget"
          :editComponent="editComponent"
        />
        <DisplayInfo
          v-if="widget.type == 'display_info'"
          :id="widget.id"
          :type="widget.type"
          :name="widget.name"
          :prefix="widget.setprefix"
          :sufix="widget.setsufix"
          :state="widget.state"
          :edit="this.edit"
          :removeFn="removeWidget"
          :allMeta="widget"
          :editComponent="editComponent"
        />
      </div>

      <div v-if="this.$store.state.user.account_type == 'admin'">
        <div
          :class="['addButton', 'deactive', this.edit ? 'close' : 'editWidget']"
          v-on:click="editWidgets"
        >
          <div v-if="!this.edit">Edytuj widgety</div>
          <div v-if="this.edit">Zakończ edycję</div>
        </div>
        <div
          class="addButton deactive"
          v-if="this.edit"
          v-on:click="this.searchWidget = true"
        >
          <div>
            &nbsp;
            <FA-Icon icon="plus" class="faicon plus" />
          </div>
        </div>
        <div
          class="addButton deactive"
          v-if="this.edit"
          @click="createWidgetsBackup()"
        >
          <div>Stwórz backup</div>
        </div>

        <div v-if="this.edit" style="width: 100%">
          <div
            v-for="(backup, idx) in backupsList"
            :key="idx"
            class="addButton deactive"
            @click="restoreWidgetsBackup(backup)"
          >
            <div>Przywróć<br />{{ backup }}</div>
          </div>
        </div>
      </div>

      <Teleport to="body">
        <SearchWidgetTemplate
          v-if="this.searchWidget"
          :closeEvent="closePanel"
          :addComponent="editComponent"
        />
        <WidgetEditor
          v-if="this.componentDict != null"
          :closeEvent="closePanel"
          :componentToAdd="componentDict"
        />
      </Teleport>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "PilotView",
  data() {
    return {
      showView: false,
      widgets: null,
      activeRefresh: true,
      edit: false,
      searchWidget: false,
      componentDict: null,
      backupsList: null,
      editRefreshTime: false,
    };
  },
  watch: {
    componentDict() {
      if (this.componentDict == null) this.loadWidgetsMeta();
    },
  },
  methods: {
    closePanel(panel) {
      if (panel == "searchWidget") this.searchWidget = false;
      if (panel == "editWidget") this.componentDict = null;
    },
    editComponent(componentDict) {
      this.closePanel("searchWidget");
      this.componentDict = componentDict;
    },
    async saveRefreshTime() {
      this.editRefreshTime = false;
      localStorage.setItem("refreshWidgetDelay", this.$store.state.refreshWidgetDelay)
      await axios
        .post(
          "dbm_api/saveSetting",
          this.$store.getters.authDict({
            setting: "refresh_widget_delay",
            value: this.$store.state.refreshWidgetDelay,
          })
        )
        .then((result) => {
          if (result.data.auth) {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err)
            this.$store.dispatch("addMsg", {
              type: "danger",
              msg: "Coś poszło nie tak z zapisem :c",
            });
          });
    },
    async loadWidgetsBackupsList() {
      await axios
        .post("pilot_api/widgetBackupsList", this.$store.getters.authDict())
        .then((result) => {
          // console.log(result.data);
          if (result.data.auth) {
            this.backupsList = result.data.backups_list;
            this.refreshData();
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    async createWidgetsBackup() {
      await axios
        .post("pilot_api/createWidgetsBackup", this.$store.getters.authDict())
        .then((result) => {
          // console.log(result.data);
          if (result.data.auth) {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    async restoreWidgetsBackup(backupName) {
      await axios
        .post(
          "pilot_api/restoreWidgetsBackup",
          this.$store.getters.authDict({ backup_name: backupName })
        )
        .then((result) => {
          // console.log(result.data);
          if (result.data.auth) {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
            this.loadWidgetsMeta();
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
    async loadWidgetsMeta() {
      await axios
        .post("pilot_api/load_widgets_meta", this.$store.getters.authDict())
        .then((result) => {
          // console.log(result.data);
          if (result.data.auth) {
            this.widgets = result.data.widgets;
            this.refreshData();
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => {
          console.log(err);  
          this.refreshData();
        });
    },
    async removeWidget(widgetID, widgetName) {
      if (
        confirm("Na pewno chcesz usunąć widget '" + widgetName + "'?") == true
      ) {
        await axios
          .post(
            "pilot_api/rmWidget",
            this.$store.getters.authDict({ widgetID: widgetID })
          )
          .then((result) => {
            // console.log(result.data);
            if (result.data.auth) {
              this.$store.dispatch("addMsg", {
                type: "info",
                msg: result.data.msg,
              });
              this.loadWidgetsMeta();
            } else this.$store.dispatch("handleLogout");
          })
          .catch((err) => console.log(err));
      }
    },
    async refreshData() {
      setTimeout(() => {
        if (this.activeRefresh) this.loadWidgetsMeta();
      }, this.$store.state.refreshWidgetDelay);
    },
    editWidgets() {
      if (this.$store.state.user.account_type == "admin") {
        this.edit = !this.edit;
        this.activeRefresh = !this.edit;
        if (this.activeRefresh) this.loadWidgetsMeta();
        if (this.edit) this.loadWidgetsBackupsList();
      }
    },
  },
  created() {
    this.$store.state.goto = '/'
    this.$store.state.currentView = "My Pilot";
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
    this.loadWidgetsMeta();
  },
  beforeUnmount() {
    this.activeRefresh = false;
  },
  components: {
    TwoStateSwitch: require("@/components/pilot_components/TwoStateSwitch.vue")
      .default,
    DisplayInfo: require("@/components/pilot_components/DisplayInfo.vue")
      .default,
    SearchWidgetTemplate:
      require("@/components/pilot_components/SearchWidgetTemplate.vue").default,
    WidgetEditor: require("@/components/pilot_components/WidgetEditor.vue")
      .default,
  },
};
</script>

<style lang="scss" scoped>
.pilot-wrapper {
  .pilotContainer {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    margin: auto;
    max-width: 500px;

    div {
      width: 50%;
    }
  }

  @media only screen and (max-width: 600px) {
    .pilotContainer {
      justify-content: center;

      div {
        width: 90%;
      }
    }
  }

  .icon{
    padding: 0 10px;
  }
  .icon:hover{
    cursor: pointer;
  }
}

.pilotMenu {
  display: flex;
  flex-direction: row;
  justify-content: center;
  padding: 10px;

  button {
    box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    margin: 3px;
  }
}

.addButton {
  min-width: calc(100% - 30px);
  border-radius: 10px;
  padding: 30px 10px;
  margin: 5px 0 0 0;
  div {
    min-width: 100%;
    text-align: center;

    .plus {
      position: absolute;
      font-size: 1.6em;
      margin-left: -0.3em;
      margin-top: -0.15em;
    }
  }
}

.close {
  background-color: rgb(219, 118, 118);
  color: #fff;
}
.editWidget {
  background-color: rgb(84, 149, 192);
  color: #fff;
}
</style>
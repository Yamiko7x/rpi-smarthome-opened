<template>
  <div
    class="deviceManagerWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <div>
      <table class="newDeviceTable">
        <tr>
          <td>Alias</td>
          <td><input type="text" v-model="alias" placeholder="local" /></td>
          <td rowspan="100%">
            <button @click="addDevice()">{{ this.actionBtn }}</button>
          </td>
        </tr>
        <tr>
          <td>IP Adres</td>
          <td><input type="text" v-model="ip" placeholder="192.168.1.2" /></td>
        </tr>
      </table>

      <table class="loopTable">
        <tr>
          <th></th>
          <th>IP Adres</th>
          <th>Alias</th>
          <th>On/Off</th>
        </tr>
        <tr v-for="(dic, alias) in devices" :key="dic.ip">
          <td class="iconCol">
            <FA-Icon icon="trash" class="trashIcon" @click="rmDevice(alias)" />
          </td>
          <td
            @click="
              this.alias = alias;
              this.ip = dic.ip;
              this.enable = dic.enable;
            "
          >
            {{ dic.ip }}
          </td>
          <td
            @click="
              this.alias = alias;
              this.ip = dic.ip;
              this.enable = dic.enable;
            "
          >
             <FA-Icon v-if="dic.work && dic.enable" title="Urządzenie pracuje" icon="cog" class="fa-spin" style="font-size: 0.9em;" />
             <FA-Icon v-else-if="!dic.work && dic.enable" title="Urządzenie poza siecią" icon="triangle-exclamation" class="" style="font-size: 0.9em;" /> 
             {{ alias }}
          </td>
          <td class="iconCol">
            <span v-if="this.axios_wait_alias != alias">
              <FA-Icon v-if="dic.enable" icon="toggle-on" class="toggleIcon factive" @click="toggleDevice(alias, 0)"/>
              <FA-Icon v-else icon="toggle-off" class="toggleIcon fdeactive" @click="toggleDevice(alias, 1)" />
            </span>
            <FA-Icon v-else icon="cog" class="toggleIcon fa-spin" />
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "DeviceManager",
  props: {
    scrollTo: { required: false, default: null },
  },
  data() {
    return {
      showView: false,
      devices: {},
      alias: "salon",
      ip: "192.168.1.101",
      enable: 0,
      actionBtn: "Dodaj",
      axios_wait_alias: '',
      activeRefresh: true,
    };
  },
  methods: {
    closeEvent() {
      this.passwdUname = null;
    },
    async toggleDevice(alias, toggle) {
      this.axios_wait_alias = alias
      await axios
        .post("actions_api/toggleDevice", this.$store.getters.authDict({alias: alias, toggle: toggle}))
        .then((result) => {
          if (result.data.auth && result.data.type=="success") {
            let deviceToggle = toggle==1 ? "Podłączone" : "Odłączone";
            this.loadDevices();
            this.$store.dispatch("addMsg", {
              type: "success",
              msg: 'Tryb urządzenia "' + alias + '": ' + deviceToggle,
            });
            console.log(result.data.running)
            this.$store.dispatch("addMsg", {
              type: result.data.running.type,
              msg: result.data.running.msg,
              time: 5000,
            });
          }
          this.axios_wait_alias = ''
        })
        .catch((err) => {
          console.log(err);
          this.axios_wait_alias = ''
        });
    },
    async loadDevices() {
      await axios
        .post("actions_api/getDevicesList", this.$store.getters.authDict())
        .then((result) => {
          if (result.data.auth) {
            console.log(result.data);
            this.devices = result.data.devices;
            
            if(this.activeRefresh){
              setTimeout(() => {
                if (this.activeRefresh) this.loadDevices();
              }, 5000);
            }
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },
    async addDevice() {
      if (this.alias && this.ip) {
        await axios
          .post(
            "actions_api/addDevice",
            this.$store.getters.authDict({ ip: this.ip, alias: this.alias, enable: this.enable })
          )
          .then((result) => {
            if (result.data.auth) {
              /* console.log(result.data); */
              this.$store.dispatch("addMsg", {
                type: "info",
                msg: result.data.msg,
              });
              this.loadDevices();
            }
          })
          .catch((err) => {
            console.log(err);
          });
      } else {
        this.$store.dispatch("addMsg", {
          type: "danger",
          msg: "Wypełnij pola.",
        });
      }
    },
    async rmDevice(alias) {
      if (this.alias) {
        if (confirm('Czy na pewno chcesz usunąć urządzenie: "'+alias+'"?')) {
        } else {
          return false
        }
        await axios
          .post(
            "actions_api/rmDevice",
            this.$store.getters.authDict({ alias: alias })
          )
          .then((result) => {
            if (result.data.auth) {
              /* console.log(result.data); */
              this.$store.dispatch("addMsg", {
                type: "info",
                msg: result.data.msg,
              });
                setTimeout(() => {
                  this.loadDevices();
                }, 2000);
            }
          })
          .catch((err) => {
            console.log(err);
          });
      } else {
        this.$store.dispatch("addMsg", {
          type: "danger",
          msg: "Wypełnij pola.",
        });
      }
    },
  },
  watch: {
    alias() {
      if (this.devices[this.alias] || this.devices[this.ip])
        this.actionBtn = "Edytuj";
      else this.actionBtn = "Dodaj";
    },
  },
  beforeUnmount() {
    this.activeRefresh = false;
  },
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
    this.loadDevices();
  },
  components: {},
};
</script>

<style lang="scss" scoped>
$color-blue: rgb(27, 77, 110);
$color-pastel-blue: rgb(179, 224, 255);
$disableGray: rgb(199, 199, 199);

.deviceManagerWrapper {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  flex-direction: column;

  .newDeviceTable {
    margin: auto;
    padding: 20px;
  }

  .loopTable {
    text-align: left;
    border-collapse: collapse;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
    width: 100%;

    td {
      padding: 5px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.2);
    }
    td:first-child {
      width: 35%;
      border-right: 1px solid rgba(0, 0, 0, 0.2);
    }
    tr th {
      padding: 5px;
      background-color: rgb(84, 149, 192);
      color: #fff;
    }
    tr {
      background-color: #fff;
      padding: 5px;
    }
    tr:hover {
      background-color: $color-pastel-blue;
      cursor: pointer;
    }

    tr td:first-child, tr td:last-child{
      width: 40px;
    }

    .iconCol {
      transition: 0.1s;
      text-align: center;

      .trashIcon, .toggleIcon {
        padding: 0 10px;
      }
      .trashIcon:hover {
        color: rgb(253, 99, 94);
      }
    }
  }
}
</style>
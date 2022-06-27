<template>
  <div class="userstable-wrapper" :class="[showView ? 'showView' : 'hideView']">
    <div class="user-profile" v-for="user in users" :key="user.uname">
      <table
        :class="{ myprofile: user.uname === this.$store.state.user.uname }"
      >
        <tr class="header" :id="user.uname">
          <td>Nickname</td>
          <td>
            <b>{{ user.uname }}</b>
          </td>
        </tr>
        <tr>
          <td>Konto</td>
          <td>{{ user.account_type }}</td>
        </tr>
        <tr>
          <td>Imię</td>
          <td>{{ user.fname }}</td>
        </tr>
        <tr>
          <td>Nazwisko</td>
          <td>{{ user.lname }}</td>
        </tr>
        <tr>
          <td>e-mail</td>
          <td>{{ user.email }}</td>
        </tr>
        <tr>
          <td>Aktywne</td>
          <td>{{ user.active }}</td>
        </tr>
        <tr>
          <td>Hasło</td>
          <td>
            <button
              class="btnInRow gray-blue"
              @click="changePassword(user.uname)"
            >
              Zmień hasło
            </button>
          </td>
        </tr>
      </table>
      <div v-if="user.uname != this.$store.state.user.uname">
        <button
          class="btn-danger"
          v-on:click="requestAxios(user.uname, 'delete')"
        >
          Usuń
        </button>
        <button
          v-if="user.active"
          class="btn-action"
          v-on:click="requestAxios(user.uname, 'block')"
        >
          Blokuj
        </button>
        <button
          v-if="!user.active"
          class="btn-yellow"
          v-on:click="requestAxios(user.uname, 'block')"
        >
          Odblokuj
        </button>
      </div>
    </div>

    <Teleport v-if="passwdUname" to="body">
      <PasswordChange :closeEvent="closeEvent" :uname="passwdUname" />
    </Teleport>

    <footer></footer>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "UsersTable",
  props: {
    scrollTo: { required: false, default: null },
  },
  data() {
    return {
      showView: false,
      users: [],
      passwdUname: null,
    };
  },
  methods: {
    closeEvent() {
      this.passwdUname = null;
    },
    changePassword(uname) {
      this.passwdUname = uname;
    },
    async loadUsers() {
      await axios
        .post("dbm_api/userslist", this.$store.getters.authDict())
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.users = result.data.users;
            setTimeout(() => {
              if (this.scrollTo != null) {
                let element = document.getElementById(this.scrollTo);
                if (element != null) {
                  element.scrollIntoView();
                  console.log("Scroll");
                }
              }
            }, this.$store.state.animationSpeed);
          } else {
            this.$store.dispatch("addMsg", {
              type: "danger",
              msg: result.data.msg,
            });
            this.$store.dispatch("handleLogout");
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },
    async requestAxios(userName, action) {
      let data = this.$store.getters.authDict({ uname: userName });
      let path = action === "delete" ? "dbm_api/deluser" : "dbm_api/blockuser";
      await axios
        .post(path, data)
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
            this.loadUsers();
          } else {
            this.$store.dispatch("addMsg", {
              type: "info",
              msg: result.data.msg,
            });
            this.$store.dispatch("handleLogout");
          }
        })
        .catch((err) => {
          console.log(err);
        });
    },
  },
  watch: {},
  created() {
    this.loadUsers();
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {
    PasswordChange: require("@/components/basic_components/PasswordChange.vue")
      .default,
  },
};
</script>

<style lang="scss" scoped>
$color-blue: rgb(27, 77, 110);
$color-pastel-blue: rgb(179, 224, 255);
$disableGray: rgb(199, 199, 199);

.userstable-wrapper {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  flex-direction: column;
}

.user-profile {
  display: flex;
  margin: auto;
  flex-direction: column;
  width: 100%;
  margin-top: 10px;

  .header {
    color: #fff;
    padding: 5px;
    background-color: $color-blue;
  }

  div {
    display: flex;
    flex-direction: row;
    width: 100%;
    button {
      width: 100%;
    }
  }

  table {
    text-align: left;
    border-collapse: collapse;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);

    td {
      padding: 5px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.2);
    }
    td:first-child {
      width: 35%;
      border-right: 1px solid rgba(0, 0, 0, 0.2);
    }
    tr {
      background-color: #fff;
    }
    tr:not(.header):hover {
      background-color: $color-pastel-blue;
    }
    tr:last-child:hover {
      background-color: #fff;
    }
    tr:last-child {
      td:last-child {
        padding: 0;
      }
    }
    .btnInRow {
      padding: 8px;
      margin: 0;
      width: 100%;
    }
  }

  .disableGray {
    tr:not(.header) {
      background-color: $disableGray;
    }
    tr:not(.header):hover {
      background-color: $disableGray;
    }
  }
  .myprofile {
    border: 0.2em solid greenyellow;
  }
}
footer {
  margin: 10px;
}
</style>
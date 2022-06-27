<template>
  <div class="passwordChangeWrapper">
    <table>
      <tr class="closeIcon">
        <td colspan="100%"><FA-Icon icon="close" class="icon" @click="this.closeEvent()" /></td>
      </tr>
      <tr>
        <td>Hasło</td>
        <td>
          <input
            :type="inType"
            :class="[this.lBorder]"
            v-model="this.passwd1"
            required
          />
        </td>
      </tr>
      <tr>
        <td>Powtórz</td>
        <td>
          <input
            :type="inType"
            :class="[this.lBorder]"
            v-model="this.passwd2"
            required
          />
        </td>
      </tr>
      <tr>
        <td>
          <button class="buttonWide" @click="showPassword()">
            <FA-Icon v-if="this.inType=='password'" icon="eye" />
            <FA-Icon v-else icon="eye-slash" />
          </button>
        </td>
        <td>
          <button class="buttonWide" @click="changePassword()">
            Zapisz nowe hasło
          </button>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "PasswordChange",
  props: {
    closeEvent: { required: true },
    uname: { required: true },
  },
  data() {
    return {
      passwd1: "Dr.Kokosik",
      passwd2: "Dr.Kokosik",
      lBorder: "borderLeftBlue",
      inType: "password",
    };
  },
  methods: {
    showPassword() {
      this.inType = this.inType == "password" ? "text" : "password";
    },
    checkCorrect(lastCheck = false) {
      if (this.passwd1 != this.passwd2) {
        this.lBorder = "borderLeftRed";
        if (lastCheck)
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Oba pola muszą zawierać jednakowe hasła.",
          });
      } else if (this.passwd1 == this.passwd2) {
        if (this.$store.state.passwdRules.test(this.passwd1)) {
          this.lBorder = "borderLeftGreen";
          return true;
        } else if (lastCheck)
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Hasło musi zawierać co najmniej 1 cyfrę, wielką literę, małą literę i mieć co najmniej 6 znaków.",
          });
      }
      return false;
    },
    async changePassword() {
      if (this.checkCorrect(true)) {
        this.closeEvent()
        await axios
          .post(
            "dbm_api/changePassword",
            this.$store.getters.authDict({ uname: this.uname , passwd: this.passwd1 })
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
            console.log(err);
          });
      }
    },
  },
  watch: {
    passwd1() {
      this.checkCorrect();
    },
    passwd2() {
      this.checkCorrect();
    },
  },
  created() {},
};
</script>

<style lang="scss" scoped>

.passwordChangeWrapper {
  position: fixed;
  z-index: 50;
  padding: 0;
  margin: 0;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.3);

  table {
    background-color: #fff;
    padding: 20px;
    padding-top: 5px;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.3);
    border: solid 2px rgb(84, 149, 192);

    .buttonWide {
      width: 100%;
    }

    .closeIcon {
      width: 100%;
      text-align: right;
      margin: 0;
      padding: 0;
    }
    .closeIcon .icon:hover{
      color: rgb(253, 99, 94);
      cursor: pointer;
    }
  }

  input {
    box-shadow: none;
  }
}
</style>
# MAPPING — textos visibles del frontend → claves i18next es-MX

Artefacto de trabajo del cambio `ui-es-mx-i18next` (grupo 1). No se embarca en el bundle.
Contrato para el `tester` (aserciones Playwright) y el `implementer` (wiring react-i18next).

Convenciones:
- Clave citada como `namespace:ruta.de.clave` (archivos en `frontend/src/locales/es-MX/<namespace>.json`).
- **[BYTE]** = texto ya en español en el código: copiado byte a byte, prohibido retocar.
- **[DECISIÓN]** = redacción donde hubo que elegir; ver notas al final.
- Interpolaciones i18next: `{{var}}`. Etiquetas `<strong>` se resuelven con `<Trans>` (las conserva por defecto).
- NO incluidos: textos que llegan del backend por `detail` del API (p. ej. "Incorrect email or password"), el texto legal del consentimiento (`consentText.text`, con sha256 en BD), placeholders no textuales (`••••••••`), números de paginación (5/10/25/50).

## common.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| varios (AddUser, EditUser, AddItem, EditItem, UserInformation) | `common:actions.save` | Save | Guardar |
| varios (todos los diálogos, UserInformation) | `common:actions.cancel` | Cancel | Cancelar |
| DeleteUser.tsx, DeleteItem.tsx, DeleteConfirmation.tsx | `common:actions.delete` | Delete | Eliminar |
| hooks/useCustomToast.ts:5 | `common:toast.successTitle` | Success! | ¡Listo! **[DECISIÓN 1]** |
| hooks/useCustomToast.ts:11 | `common:toast.errorTitle` | Something went wrong! | ¡Algo salió mal! |
| utils.ts:14 (fallback de `extractErrorMessage`) | `common:errors.generic` | Something went wrong. | Algo salió mal. |
| login.tsx:28, signup.tsx:25, recover-password.tsx:28, AddUser.tsx:36, EditUser.tsx:36, UserInformation.tsx:26 | `common:validation.emailInvalid` | Invalid email address | Correo electrónico no válido |
| login.tsx:31, signup.tsx:29, reset-password.tsx:36, AddUser.tsx:40, ChangePassword.tsx:24,28 | `common:validation.passwordRequired` | Password is required | La contraseña es obligatoria |
| login.tsx:32, signup.tsx:30, reset-password.tsx:37, AddUser.tsx:41, EditUser.tsx:40, ChangePassword.tsx:25,29 | `common:validation.passwordMinLength` | Password must be at least 8 characters | La contraseña debe tener al menos 8 caracteres |
| signup.tsx:33, reset-password.tsx:40, ChangePassword.tsx:32 | `common:validation.passwordConfirmationRequired` | Password confirmation is required | Debes confirmar la contraseña |
| AddUser.tsx:44 | `common:validation.confirmPasswordPrompt` | Please confirm your password | Confirma tu contraseña |
| signup.tsx:36, reset-password.tsx:43, AddUser.tsx:49, EditUser.tsx:48, ChangePassword.tsx:35 | `common:validation.passwordsDontMatch` | The passwords don't match | Las contraseñas no coinciden |
| signup.tsx:26 | `common:validation.fullNameRequired` | Full Name is required | El nombre completo es obligatorio |
| Items/AddItem.tsx:34, Items/EditItem.tsx:34 | `common:validation.titleRequired` | Title is required | El título es obligatorio |
| Admin/columns.tsx:70, Items/columns.tsx:67, PendingUsers.tsx:20, PendingItems.tsx:19 (sr-only) | `common:table.actions` | Actions | Acciones |
| Common/DataTable.tsx:94 | `common:table.noResults` | No results found. | No se encontraron resultados. |
| Admin/columns.tsx:24, UserInformation.tsx:112 | `common:table.notAvailable` | N/A | N/D **[DECISIÓN 2]** |
| Common/DataTable.tsx:105-117 | `common:table.pagination.showingEntries` | Showing {from} to {to} of {total} entries | Mostrando {{from}} a {{to}} de {{total}} registros |
| Common/DataTable.tsx:120 | `common:table.pagination.rowsPerPage` | Rows per page | Filas por página |
| Common/DataTable.tsx:143-150 | `common:table.pagination.pageOf` | Page {page} of {total} | Página {{page}} de {{total}} |
| Common/DataTable.tsx:161 (sr-only) | `common:table.pagination.goToFirstPage` | Go to first page | Ir a la primera página |
| Common/DataTable.tsx:171 (sr-only) | `common:table.pagination.goToPreviousPage` | Go to previous page | Ir a la página anterior |
| Common/DataTable.tsx:181 (sr-only) | `common:table.pagination.goToNextPage` | Go to next page | Ir a la página siguiente |
| Common/DataTable.tsx:191 (sr-only) | `common:table.pagination.goToLastPage` | Go to last page | Ir a la última página |
| Common/ErrorComponent.tsx:13 | `common:errorPage.code` | Error | Error |
| Common/ErrorComponent.tsx:15 | `common:errorPage.oops` | Oops! | ¡Ups! |
| Common/ErrorComponent.tsx:20 | `common:errorPage.message` | Something went wrong. Please try again. | Algo salió mal. Inténtalo de nuevo. |
| Common/ErrorComponent.tsx:23 | `common:errorPage.goHome` | Go Home | Ir al inicio |
| Common/NotFound.tsx:13 | `common:notFoundPage.code` | 404 | 404 |
| Common/NotFound.tsx:15 | `common:notFoundPage.oops` | Oops! | ¡Ups! |
| Common/NotFound.tsx:20 | `common:notFoundPage.message` | The page you are looking for was not found. | No encontramos la página que buscas. |
| Common/NotFound.tsx:24 | `common:notFoundPage.goBack` | Go Back | Volver |
| Common/Logo.tsx:32,40,50 (alt) | `common:logoAlt` | FastAPI | FastAPI (marca, sin traducir) |

## auth.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| routes/login.tsx:49 (meta title) | `auth:login.pageTitle` | Log In - FastAPI Template | Iniciar sesión - FastAPI Template |
| routes/login.tsx:80 | `auth:login.title` | Login to your account | Inicia sesión en tu cuenta |
| routes/login.tsx:89 | `auth:login.emailLabel` | Email | Correo electrónico |
| routes/login.tsx:93 | `auth:login.emailPlaceholder` | user@example.com | usuario@ejemplo.com **[DECISIÓN 3]** |
| routes/login.tsx:109 | `auth:login.passwordLabel` | Password | Contraseña |
| routes/login.tsx:120 | `auth:login.passwordPlaceholder` | Password | Contraseña |
| routes/login.tsx:114 | `auth:login.forgotPassword` | Forgot your password? | ¿Olvidaste tu contraseña? |
| routes/login.tsx:130 | `auth:login.submit` | Log In | Iniciar sesión |
| routes/login.tsx:135 | `auth:login.orSeparator` | o (ya en minúscula en el código; CSS lo muestra en mayúscula) | o **[BYTE]** |
| routes/login.tsx:152 | `auth:login.continueWithGoogle` | Continuar con Google (ya en español) | Continuar con Google **[BYTE]** |
| routes/login.tsx:157 | `auth:login.noAccount` | Don't have an account yet? | ¿Aún no tienes una cuenta? |
| routes/login.tsx:159 | `auth:login.signUpLink` | Sign up | Regístrate |
| routes/signup.tsx:54 (meta title) | `auth:signup.pageTitle` | Sign Up - FastAPI Template | Crear cuenta - FastAPI Template |
| routes/signup.tsx:90 | `auth:signup.title` | Create an account | Crea una cuenta |
| routes/signup.tsx:99 | `auth:signup.fullNameLabel` | Full Name | Nombre completo |
| routes/signup.tsx:103 | `auth:signup.fullNamePlaceholder` | User | Usuario |
| routes/signup.tsx:118 | `auth:signup.emailLabel` | Email | Correo electrónico |
| routes/signup.tsx:122 | `auth:signup.emailPlaceholder` | user@example.com | usuario@ejemplo.com |
| routes/signup.tsx:137 | `auth:signup.passwordLabel` | Password | Contraseña |
| routes/signup.tsx:141 | `auth:signup.passwordPlaceholder` | Password | Contraseña |
| routes/signup.tsx:155 | `auth:signup.confirmPasswordLabel` | Confirm Password | Confirmar contraseña |
| routes/signup.tsx:159 | `auth:signup.confirmPasswordPlaceholder` | Confirm Password | Confirmar contraseña |
| routes/signup.tsx:173 | `auth:signup.submit` | Sign Up | Crear cuenta **[DECISIÓN 4]** |
| routes/signup.tsx:178 | `auth:signup.alreadyHaveAccount` | Already have an account? | ¿Ya tienes una cuenta? |
| routes/signup.tsx:180 | `auth:signup.logInLink` | Log in | Inicia sesión |
| routes/recover-password.tsx:45 (meta title) | `auth:recoverPassword.pageTitle` | Recover Password - FastAPI Template | Recuperar contraseña - FastAPI Template |
| routes/recover-password.tsx:88 | `auth:recoverPassword.title` | Password Recovery | Recuperación de contraseña |
| routes/recover-password.tsx:97 | `auth:recoverPassword.emailLabel` | Email | Correo electrónico |
| routes/recover-password.tsx:101 | `auth:recoverPassword.emailPlaceholder` | user@example.com | usuario@ejemplo.com |
| routes/recover-password.tsx:116 | `auth:recoverPassword.submit` | Continue | Continuar |
| routes/recover-password.tsx:121 | `auth:recoverPassword.rememberPassword` | Remember your password? | ¿Recuerdas tu contraseña? |
| routes/recover-password.tsx:122 | `auth:recoverPassword.logInLink` | Log in | Inicia sesión |
| routes/recover-password.tsx:69 (toast) | `auth:recoverPassword.successToast` | Password recovery email sent successfully | Te enviamos un correo para recuperar tu contraseña |
| routes/reset-password.tsx:63 (meta title) | `auth:resetPassword.pageTitle` | Reset Password - FastAPI Template | Restablecer contraseña - FastAPI Template |
| routes/reset-password.tsx:107 | `auth:resetPassword.title` | Reset Password | Restablecer contraseña |
| routes/reset-password.tsx:116 | `auth:resetPassword.newPasswordLabel` | New Password | Nueva contraseña |
| routes/reset-password.tsx:120 | `auth:resetPassword.newPasswordPlaceholder` | New Password | Nueva contraseña |
| routes/reset-password.tsx:134 | `auth:resetPassword.confirmPasswordLabel` | Confirm Password | Confirmar contraseña |
| routes/reset-password.tsx:138 | `auth:resetPassword.confirmPasswordPlaceholder` | Confirm Password | Confirmar contraseña |
| routes/reset-password.tsx:152 | `auth:resetPassword.submit` | Reset Password | Restablecer contraseña |
| routes/reset-password.tsx:157 | `auth:resetPassword.rememberPassword` | Remember your password? | ¿Recuerdas tu contraseña? |
| routes/reset-password.tsx:158 | `auth:resetPassword.logInLink` | Log in | Inicia sesión |
| routes/reset-password.tsx:88 (toast) | `auth:resetPassword.successToast` | Password updated successfully | Contraseña actualizada correctamente |
| routes/google-callback.tsx:11 (meta title) | `auth:googleCallback.pageTitle` | Google - FastAPI Template | Google - FastAPI Template |
| routes/google-callback.tsx:39 (toast) | `auth:googleCallback.errorToast` | No se pudo iniciar sesión con Google (ya en español) | No se pudo iniciar sesión con Google **[BYTE]** |

## layout.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| Sidebar/AppSidebar.tsx:16 (menú + tooltip) | `layout:sidebar.dashboard` | Dashboard | Panel |
| Sidebar/AppSidebar.tsx:17 (menú + tooltip) | `layout:sidebar.items` | Items | Elementos |
| Sidebar/AppSidebar.tsx:24 (menú + tooltip) | `layout:sidebar.admin` | Admin | Administración |
| Common/Appearance.tsx:34 (tooltip),36 | `layout:sidebar.appearance` | Appearance | Apariencia |
| Common/Appearance.tsx:37,79 (sr-only) | `layout:sidebar.toggleTheme` | Toggle theme | Cambiar tema |
| Common/Appearance.tsx:50,88 | `layout:sidebar.themeLight` | Light | Claro |
| Common/Appearance.tsx:57,95 | `layout:sidebar.themeDark` | Dark | Oscuro |
| Common/Appearance.tsx:61,99 | `layout:sidebar.themeSystem` | System | Sistema |
| Sidebar/User.tsx:85 | `layout:sidebar.userSettings` | User Settings | Configuración de usuario |
| Sidebar/User.tsx:90 | `layout:sidebar.logOut` | Log Out | Cerrar sesión |
| Sidebar/User.tsx:32 (fallback de iniciales del avatar) | `layout:sidebar.userFallbackName` | User | Usuario **[DECISIÓN 5]** |
| Common/Footer.tsx:25 | `layout:footer.copyright` | Full Stack FastAPI Template - {year} | Full Stack FastAPI Template - {{year}} (nombre del template, sin traducir) |
| Common/Footer.tsx:8 (aria-label) | `layout:footer.githubAria` | GitHub | GitHub (marca) |
| Common/Footer.tsx:10 (aria-label) | `layout:footer.xAria` | X | X (marca) |
| Common/Footer.tsx:14 (aria-label) | `layout:footer.linkedinAria` | LinkedIn | LinkedIn (marca) |
| routes/_layout/index.tsx:11 (meta title) | `layout:dashboard.pageTitle` | Dashboard - FastAPI Template | Panel - FastAPI Template |
| routes/_layout/index.tsx:24 | `layout:dashboard.greeting` | Hi, {name} 👋 | Hola, {{name}} 👋 (var: `full_name \|\| email`) |
| routes/_layout/index.tsx:27 | `layout:dashboard.welcomeBack` | Welcome back, nice to see you again!!! | ¡Qué gusto verte de nuevo! **[DECISIÓN 6]** |

## items.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| routes/_layout/items.tsx:25 (meta title) | `items:page.pageTitle` | Items - FastAPI Template | Elementos - FastAPI Template |
| routes/_layout/items.tsx:62 | `items:page.title` | Items | Elementos |
| routes/_layout/items.tsx:63 | `items:page.subtitle` | Create and manage your items | Crea y administra tus elementos |
| routes/_layout/items.tsx:40 | `items:empty.title` | You don't have any items yet | Aún no tienes elementos |
| routes/_layout/items.tsx:41 | `items:empty.description` | Add a new item to get started | Agrega un elemento nuevo para comenzar |
| Items/columns.tsx:38, PendingItems.tsx:15 | `items:table.idHeader` | ID | ID |
| Items/columns.tsx:43, PendingItems.tsx:16 | `items:table.titleHeader` | Title | Título |
| Items/columns.tsx:50, PendingItems.tsx:17 | `items:table.descriptionHeader` | Description | Descripción |
| Items/columns.tsx:60 | `items:table.noDescription` | No description | Sin descripción |
| Items/columns.tsx:29 (sr-only) | `items:table.copyId` | Copy ID | Copiar ID |
| Items/AddItem.tsx:77 | `items:addItem.button` | Add Item | Agregar elemento |
| Items/AddItem.tsx:82 | `items:addItem.dialogTitle` | Add Item | Agregar elemento |
| Items/AddItem.tsx:84 | `items:addItem.dialogDescription` | Fill in the details to add a new item. | Completa los datos para agregar un elemento nuevo. |
| Items/AddItem.tsx:96 | `items:addItem.titleLabel` | Title | Título |
| Items/AddItem.tsx:100 | `items:addItem.titlePlaceholder` | Title | Título |
| Items/AddItem.tsx:116 | `items:addItem.descriptionLabel` | Description | Descripción |
| Items/AddItem.tsx:118 | `items:addItem.descriptionPlaceholder` | Description | Descripción |
| Items/AddItem.tsx:58 (toast) | `items:addItem.successToast` | Item created successfully | Elemento creado correctamente |
| Items/EditItem.tsx:85 | `items:editItem.menuItem` | Edit Item | Editar elemento |
| Items/EditItem.tsx:91 | `items:editItem.dialogTitle` | Edit Item | Editar elemento |
| Items/EditItem.tsx:93 | `items:editItem.dialogDescription` | Update the item details below. | Actualiza los datos del elemento. |
| Items/EditItem.tsx:103 | `items:editItem.titleLabel` | Title | Título |
| Items/EditItem.tsx:106 | `items:editItem.titlePlaceholder` | Title | Título |
| Items/EditItem.tsx:118 | `items:editItem.descriptionLabel` | Description | Descripción |
| Items/EditItem.tsx:120 | `items:editItem.descriptionPlaceholder` | Description | Descripción |
| Items/EditItem.tsx:64 (toast) | `items:editItem.successToast` | Item updated successfully | Elemento actualizado correctamente |
| Items/DeleteItem.tsx:62 | `items:deleteItem.menuItem` | Delete Item | Eliminar elemento |
| Items/DeleteItem.tsx:67 | `items:deleteItem.dialogTitle` | Delete Item | Eliminar elemento |
| Items/DeleteItem.tsx:69-70 | `items:deleteItem.dialogDescription` | This item will be permanently deleted. Are you sure? You will not be able to undo this action. | Este elemento se eliminará permanentemente. ¿Estás seguro? No podrás deshacer esta acción. |
| Items/DeleteItem.tsx:40 (toast) | `items:deleteItem.successToast` | The item was deleted successfully | El elemento se eliminó correctamente |

## admin.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| routes/_layout/admin.tsx:33 (meta title) | `admin:page.pageTitle` | Admin - FastAPI Template | Administración - FastAPI Template |
| routes/_layout/admin.tsx:64 | `admin:page.title` | Users | Usuarios |
| routes/_layout/admin.tsx:66 | `admin:page.subtitle` | Manage user accounts and permissions | Administra las cuentas de usuario y sus permisos |
| Admin/columns.tsx:16, PendingUsers.tsx:15 | `admin:table.fullNameHeader` | Full Name | Nombre completo |
| Admin/columns.tsx:37, PendingUsers.tsx:16 | `admin:table.emailHeader` | Email | Correo electrónico |
| Admin/columns.tsx:44, PendingUsers.tsx:17 | `admin:table.roleHeader` | Role | Rol |
| Admin/columns.tsx:53, PendingUsers.tsx:18 | `admin:table.statusHeader` | Status | Estado |
| Admin/columns.tsx:28 (badge) | `admin:table.youBadge` | You | Tú |
| Admin/columns.tsx:47 | `admin:table.roleSuperuser` | Superuser | Superusuario |
| Admin/columns.tsx:47 | `admin:table.roleUser` | User | Usuario |
| Admin/columns.tsx:63 | `admin:table.statusActive` | Active | Activo |
| Admin/columns.tsx:63 | `admin:table.statusInactive` | Inactive | Inactivo |
| Admin/AddUser.tsx:96 | `admin:addUser.button` | Add User | Agregar usuario |
| Admin/AddUser.tsx:101 | `admin:addUser.dialogTitle` | Add User | Agregar usuario |
| Admin/AddUser.tsx:103 | `admin:addUser.dialogDescription` | Fill in the form below to add a new user to the system. | Completa el formulario para agregar un usuario nuevo al sistema. |
| Admin/AddUser.tsx:115 | `admin:addUser.emailLabel` | Email | Correo electrónico |
| Admin/AddUser.tsx:119 | `admin:addUser.emailPlaceholder` | Email | Correo electrónico |
| Admin/AddUser.tsx:135 | `admin:addUser.fullNameLabel` | Full Name | Nombre completo |
| Admin/AddUser.tsx:137 | `admin:addUser.fullNamePlaceholder` | Full name | Nombre completo |
| Admin/AddUser.tsx:150 | `admin:addUser.setPasswordLabel` | Set Password | Asignar contraseña |
| Admin/AddUser.tsx:154 | `admin:addUser.passwordPlaceholder` | Password | Contraseña |
| Admin/AddUser.tsx:171 | `admin:addUser.confirmPasswordLabel` | Confirm Password | Confirmar contraseña |
| Admin/AddUser.tsx:176 | `admin:addUser.confirmPasswordPlaceholder` | Password | Contraseña |
| Admin/AddUser.tsx:198 | `admin:addUser.isSuperuserLabel` | Is superuser? | ¿Es superusuario? |
| Admin/AddUser.tsx:214 | `admin:addUser.isActiveLabel` | Is active? | ¿Está activo? |
| Admin/AddUser.tsx:77 (toast) | `admin:addUser.successToast` | User created successfully | Usuario creado correctamente |
| Admin/EditUser.tsx:106 | `admin:editUser.menuItem` | Edit User | Editar usuario |
| Admin/EditUser.tsx:112 | `admin:editUser.dialogTitle` | Edit User | Editar usuario |
| Admin/EditUser.tsx:114 | `admin:editUser.dialogDescription` | Update the user details below. | Actualiza los datos del usuario. |
| Admin/EditUser.tsx:124 | `admin:editUser.emailLabel` | Email | Correo electrónico |
| Admin/EditUser.tsx:128 | `admin:editUser.emailPlaceholder` | Email | Correo electrónico |
| Admin/EditUser.tsx:144 | `admin:editUser.fullNameLabel` | Full Name | Nombre completo |
| Admin/EditUser.tsx:146 | `admin:editUser.fullNamePlaceholder` | Full name | Nombre completo |
| Admin/EditUser.tsx:158 | `admin:editUser.setPasswordLabel` | Set Password | Asignar contraseña |
| Admin/EditUser.tsx:161 | `admin:editUser.passwordPlaceholder` | Password | Contraseña |
| Admin/EditUser.tsx:176 | `admin:editUser.confirmPasswordLabel` | Confirm Password | Confirmar contraseña |
| Admin/EditUser.tsx:179 | `admin:editUser.confirmPasswordPlaceholder` | Password | Contraseña |
| Admin/EditUser.tsx:200 | `admin:editUser.isSuperuserLabel` | Is superuser? | ¿Es superusuario? |
| Admin/EditUser.tsx:216 | `admin:editUser.isActiveLabel` | Is active? | ¿Está activo? |
| Admin/EditUser.tsx:80 (toast) | `admin:editUser.successToast` | User updated successfully | Usuario actualizado correctamente |
| Admin/DeleteUser.tsx:62 | `admin:deleteUser.menuItem` | Delete User | Eliminar usuario |
| Admin/DeleteUser.tsx:67 | `admin:deleteUser.dialogTitle` | Delete User | Eliminar usuario |
| Admin/DeleteUser.tsx:69-71 | `admin:deleteUser.dialogDescription` | All items associated with this user will also be **permanently deleted.** Are you sure? You will not be able to undo this action. | Todos los elementos asociados a este usuario también se eliminarán `<strong>`permanentemente`</strong>`. ¿Estás seguro? No podrás deshacer esta acción. (vía `<Trans>`) |
| Admin/DeleteUser.tsx:40 (toast) | `admin:deleteUser.successToast` | The user was deleted successfully | El usuario se eliminó correctamente |

## settings.json

| Archivo fuente | Clave | Inglés original | es-MX |
|---|---|---|---|
| routes/_layout/settings.tsx:20 (meta title) | `settings:page.pageTitle` | Settings - FastAPI Template | Configuración - FastAPI Template |
| routes/_layout/settings.tsx:39 | `settings:page.title` | User Settings | Configuración de usuario |
| routes/_layout/settings.tsx:41 | `settings:page.subtitle` | Manage your account settings and preferences | Administra la configuración y preferencias de tu cuenta |
| routes/_layout/settings.tsx:10 | `settings:tabs.myProfile` | My profile | Mi perfil |
| routes/_layout/settings.tsx:11 | `settings:tabs.password` | Password | Contraseña |
| routes/_layout/settings.tsx:12 | `settings:tabs.dangerZone` | Danger zone | Zona de riesgo |
| UserSettings/UserInformation.tsx:85 | `settings:userInformation.title` | User Information | Información del usuario |
| UserSettings/UserInformation.tsx:97,105 | `settings:userInformation.fullNameLabel` | Full name | Nombre completo |
| UserSettings/UserInformation.tsx:125,133 | `settings:userInformation.emailLabel` | Email | Correo electrónico |
| UserSettings/UserInformation.tsx:112 | `settings:userInformation.notAvailable` | N/A | N/D |
| UserSettings/UserInformation.tsx:148 | `settings:userInformation.save` | Save | Guardar |
| UserSettings/UserInformation.tsx:156 | `settings:userInformation.cancel` | Cancel | Cancelar |
| UserSettings/UserInformation.tsx:161 | `settings:userInformation.edit` | Edit | Editar |
| UserSettings/UserInformation.tsx:55 (toast) | `settings:userInformation.successToast` | User updated successfully | Usuario actualizado correctamente |
| UserSettings/ChangePassword.tsx:70 | `settings:changePassword.title` | Change Password | Cambiar contraseña |
| UserSettings/ChangePassword.tsx:81 | `settings:changePassword.currentPasswordLabel` | Current Password | Contraseña actual |
| UserSettings/ChangePassword.tsx:100 | `settings:changePassword.newPasswordLabel` | New Password | Nueva contraseña |
| UserSettings/ChangePassword.tsx:119 | `settings:changePassword.confirmPasswordLabel` | Confirm Password | Confirmar contraseña |
| UserSettings/ChangePassword.tsx:138 | `settings:changePassword.submit` | Update Password | Actualizar contraseña |
| UserSettings/ChangePassword.tsx:58 (toast) | `settings:changePassword.successToast` | Password updated successfully | Contraseña actualizada correctamente |
| UserSettings/DeleteAccount.tsx:6 | `settings:deleteAccount.title` | Delete Account | Eliminar cuenta |
| UserSettings/DeleteAccount.tsx:8 | `settings:deleteAccount.description` | Permanently delete your account and all associated data. | Elimina permanentemente tu cuenta y todos los datos asociados. |
| UserSettings/DeleteConfirmation.tsx:47 | `settings:deleteAccount.button` | Delete Account | Eliminar cuenta |
| UserSettings/DeleteConfirmation.tsx:53 | `settings:deleteAccount.confirmTitle` | Confirmation Required | Confirmación requerida |
| UserSettings/DeleteConfirmation.tsx:55-58 | `settings:deleteAccount.confirmDescription` | All your account data will be **permanently deleted.** If you are sure, please click **"Confirm"** to proceed. This action cannot be undone. | Todos los datos de tu cuenta se eliminarán `<strong>`permanentemente`</strong>`. Si estás seguro, haz clic en `<strong>`"Eliminar"`</strong>` para continuar. Esta acción no se puede deshacer. (vía `<Trans>`) **[DECISIÓN 7]** |
| UserSettings/DeleteConfirmation.tsx:73 | `settings:deleteAccount.confirmButton` | Delete | Eliminar |
| UserSettings/DeleteConfirmation.tsx:64 | `settings:deleteAccount.cancel` | Cancel | Cancelar |
| UserSettings/DeleteConfirmation.tsx:30 (toast) | `settings:deleteAccount.successToast` | Your account has been successfully deleted | Tu cuenta se eliminó correctamente |

## consent.json (todo [BYTE]: ya en español en Consent/ConsentGate.tsx)

| Archivo fuente | Clave | Texto original (ya es-MX) | es-MX |
|---|---|---|---|
| Consent/ConsentGate.tsx:56-58 | `consent:gate.title` | Consentimiento para el tratamiento de datos de salud | (idéntico) **[BYTE]** |
| Consent/ConsentGate.tsx:60-62 | `consent:gate.description` | Antes de capturar cualquier dato de salud necesitamos tu consentimiento expreso (versión {consentText.version}). | Antes de capturar cualquier dato de salud necesitamos tu consentimiento expreso (versión {{version}}). **[BYTE]** (solo se parametriza la versión) |
| Consent/ConsentGate.tsx:75 | `consent:gate.acceptButton` | Acepto el tratamiento de mis datos sensibles | (idéntico) **[BYTE]** |
| Consent/ConsentGate.tsx:43 (toast) | `consent:gate.successToast` | Consentimiento registrado | (idéntico) **[BYTE]** |

El cuerpo legal del consentimiento (`consentText.text`) llega del backend y tiene sha256 en BD: **no va en los JSON**.

## Exclusiones deliberadas

- `frontend/src/components/ui/` (primitivas shadcn) y `frontend/src/client/` (generado): fuera de alcance.
- Mensajes de error del API que llegan por `detail` (p. ej. "Incorrect email or password"): se muestran tal cual, no se traducen en frontend.
- Placeholder `••••••••` (ChangePassword.tsx): no es texto.
- Opciones numéricas de paginación 5/10/25/50 (DataTable.tsx:131): números.
- `getInitials` produce iniciales, no texto traducible (salvo el fallback "User", cubierto en `layout:sidebar.userFallbackName`).
- theme-provider.tsx, Common/AuthLayout.tsx, Sidebar/Main.tsx, hooks/useCopyToClipboard.ts, hooks/useMobile.ts: sin strings visibles propios.
- `full_name` max 30 (UserInformation.tsx:25): zod sin mensaje custom; el mensaje por defecto de zod queda fuera del contrato (no hay texto en el código fuente).

## Decisiones de redacción (para revisión humana)

1. **Toast "Success!" → "¡Listo!"**: "¡Éxito!" suena literal y robótico en es-MX; "¡Listo!" es el patrón habitual en apps mexicanas. Alternativa si se prefiere literal: "¡Éxito!".
2. **"N/A" → "N/D"** (no disponible): convención es; si el equipo prefiere conservar "N/A" (también usado en es), cambiar en `common:table.notAvailable` y `settings:userInformation.notAvailable`.
3. **Placeholder "user@example.com" → "usuario@ejemplo.com"**: se traduce el ejemplo; nota: `ejemplo.com` no es dominio reservado como `example.com`. Si eso importa, usar "usuario@example.com".
4. **Botón de signup "Sign Up" → "Crear cuenta"** (y el enlace desde login "Sign up" → "Regístrate"): el botón confirma la acción del título "Crea una cuenta"; el enlace invita. Deliberadamente distintos.
5. **Fallback de avatar "User" → "Usuario"**: cambia las iniciales del fallback de "U" a "U" (sin efecto visible real).
6. **"Welcome back, nice to see you again!!!" → "¡Qué gusto verte de nuevo!"**: se eliminó la triple exclamación (no profesional) y se evitó "Bienvenido" por género. Neutral y con tuteo.
7. **DeleteConfirmation**: el inglés dice haz clic en "Confirm" pero el botón real dice "Delete". Se resolvió la inconsistencia del original: la traducción dice "Eliminar", igual que el botón (`settings:deleteAccount.confirmButton`). Si se prefiere fidelidad al original, usar "Confirmar".
8. **"Dashboard" → "Panel"**: alternativas "Inicio" o "Tablero"; "Panel" es corto y estándar.
9. **"Danger zone" → "Zona de riesgo"**: alternativa "Zona de peligro" (más literal); "riesgo" suena menos alarmista y es común en UI es-MX.
10. **"Admin" (sidebar) → "Administración"**: el título de la página es "Usuarios" (traducción de "Users"); el ítem del menú usa el sustantivo completo.
11. **Toasts de éxito "… successfully" → "… correctamente"**: patrón uniforme en todos los namespaces.
12. **"entries" (paginación) → "registros"**: alternativa "resultados"; "registros" distingue del mensaje "No se encontraron resultados.".

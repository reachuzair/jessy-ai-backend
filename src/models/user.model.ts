import { Model, DataTypes, UUIDV4 } from "sequelize";
import bcrypt from "bcrypt";
import { sequelize } from "../config/db";

export interface IUser {
  id?: string;
  email: string;
  name?: string;
  password?: string;
  role?: "user" | "admin";
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IUserCreate
  extends Omit<IUser, "id" | "createdAt" | "updatedAt"> {
  email: string;
  password?: string;
}

export interface IUserUpdate
  extends Partial<Omit<IUser, "id" | "createdAt" | "updatedAt">> {}

class User extends Model<IUser, IUserCreate> implements IUser {
  public id!: string;
  public email!: string;
  public name?: string;
  public password?: string;
  public role?: "user" | "admin";
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;

  // Instance methods
  async comparePassword(candidatePassword: string): Promise<boolean> {
    if (!this.password) return false;
    return bcrypt.compare(candidatePassword, this.password);
  }

  async hashPassword(): Promise<void> {
    if (this.password && this.changed("password")) {
      this.password = await bcrypt.hash(this.password, 15);
    }
  }
}

User.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: UUIDV4,
      primaryKey: true,
      allowNull: false,
    },
    email: {
      type: DataTypes.STRING(255),
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true,
      },
    },
    name: {
      type: DataTypes.STRING(255),
      allowNull: true,
    },
    password: {
      type: DataTypes.STRING(255),
      allowNull: true,
    },
    role: {
      type: DataTypes.ENUM("user", "admin"),
      defaultValue: "user",
    },
  },
  {
    sequelize,
    tableName: "users",
    modelName: "User",
    timestamps: true,
    hooks: {
      beforeSave: async (user: User) => {
        await user.hashPassword();
      },
    },
    indexes: [
      {
        unique: true,
        fields: ["email"],
        name: "idx_users_email_unique",
      },
      {
        fields: ["role"],
        name: "idx_users_role",
      },
      {
        fields: ["created_at"],
        name: "idx_users_created_at",
      },
      {
        fields: ["updated_at"],
        name: "idx_users_updated_at",
      },
    ],
  }
);

export default User;
